# -*- coding: utf-8 -*-
from copy import copy, deepcopy
from .Utils import *
from .Enums import *
from .Card import *


class Action:
    name = "Unknown Action"

    def __init__(self):
        pass

    def __repr__(self):
        return self.name

    def act(self, state, log):
        return None


# Conditionals and other stuff


class nothing(Action):
    name = "Do Nothing"

    def act(self, state, log):
        state = deepcopy(state)
        state.candidates = [state.stack.pop()]
        return state


class maybe(Action):
    name = "Maybe"

    def __init__(self, action):
        self.action = action

    def act(self, state, log):
        state = deepcopy(state)
        state.candidates = [nothing(), self.action]
        return state


class hasCards(Action):
    def __init__(self, action, zone=PlayerZones.HAND):
        self.zone = zone
        self.action = action

    def act(self, state, log):
        if state.zoneCount(self.zone) > 0:
            return self.action.act(state, log)
        else:
            state = deepcopy(state)
            state.candidates = [state.stack.pop()]
            return state


# Predicate-associated actions


class startGame(Action):
    name = "Start Game"

    def act(self, state, log):
        if log[state.logLine].pred == "GAME_META_INFO":
            state = deepcopy(state)
            state.logLine += 1
            state.candidates = [startDecks()]
            return state
        else:
            return None


class startDecks(Action):
    name = "Start With"

    def act(self, state, log):
        logLine = log[state.logLine]
        if logLine.pred == "STARTS_WITH":
            state = deepcopy(state)
            state.player = logLine.player
            if not state.moveCards(
                logLine.items, NeutralZones.SUPPLY, PlayerZones.DISCARD
            ):
                return None

            state.logLine += 1
            state.candidates = [gameStartDraw(), startDecks()]
            return state
        else:
            return None


class gameStartDraw(Action):
    name = "Initial Draw"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player
        state.stack = [newTurn()]
        state.stack += [drawN(5) for i in range(PLAYER_COUNT)]
        state.candidates = [state.stack.pop()]
        return state


class shuffle(Action):
    name = "Shuffle"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player
        if logLine.pred == "SHUFFLES":
            state.moveAllCards(PlayerZones.DISCARD, PlayerZones.DECK)
            if state.stack:
                state.logLine += 1
                state.candidates = [state.stack.pop()]
                return state
        return None


class drawN(Action):
    name = "Draw N"

    def __init__(self, n, player=-1):
        self.n = n
        self.name = "Draw {} {}".format(n, player)
        self.player = player

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        if self.player == -1:
            state.player = logLine.player
        else:
            state.player = self.player
        deckCount = state.zoneCount(PlayerZones.DECK)
        discardCount = state.zoneCount(PlayerZones.DISCARD)

        if deckCount < self.n and discardCount > 0:
            # Shuffle then go again
            state.candidates = [shuffle()]
            state.stack += [self]
            return state
        elif deckCount > 0:
            if log[state.logLine].pred == "DRAW":
                state.logLine += 1
                if not state.moveCards(
                    logLine.items, PlayerZones.DECK, PlayerZones.HAND
                ):
                    return None
            else:
                return None
        state.candidates = [state.stack.pop()]
        return state


class revealN(Action):
    name = "Reveal N"

    def __init__(self, n):
        self.n = n
        self.name = "Reveal {}".format(n)

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player
        deckCount = state.zoneCount(PlayerZones.DECK)
        discardCount = state.zoneCount(PlayerZones.DISCARD)

        if deckCount < self.n and discardCount > 0:
            # Shuffle then go again
            state.candidates = [shuffle()]
            state.stack += [self]
            return state
        elif deckCount > 0:
            if log[state.logLine].pred == "REVEAL":
                state.logLine += 1
                if not state.moveCards(
                    logLine.items, PlayerZones.DECK, PlayerZones.DECK
                ):
                    return None
            else:
                return None
        state.candidates = [state.stack.pop()]
        return state


class newTurn(Action):
    name = "New Turn"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        if logLine.pred == "NEW_TURN":
            state.player = logLine.player
            state.logLine += 1
            state.candidates = [actionPhase(), startOfTurn()]

            state.actions, state.buys, state.coins = (1, 1, 0)
            state.potions, state.reductions = (0, 0)
            return state
        else:
            return None


class startOfTurn(Action):
    name = "Turn Start"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        if logLine.pred == "STARTS_TURN":
            state.player = logLine.player
            state.logLine += 1
            state.candidates = [actionPhase()]
            state.candidates += [onDuration(d[0]) for d in state.turnStarts]
            state.stack = [startOfTurn()]
            return state
        else:
            return None


class onDuration(Action):
    def __init__(self, target):
        self.name = "On Duration {}".format(target)
        self.target = target

    def act(self, state, log):
        state = deepcopy(state)
        cardInfo = getCardInfo(self.target)
        if hasattr(cardInfo, "onDuration"):
            return cardInfo.onDuration(state, log)
        else:
            state.candidates = [state.stack.pop()]
            return state


class actionPhase(Action):
    name = "Action Phase"

    def act(self, state, log):
        state = deepcopy(state)
        state.player = log[state.logLine].player
        state.stack = [actionPhase()]
        state.candidates = [buyPhaseA(), actionPlayNormal()]

        return state


class actionPlayNormal(Action):
    name = "Play Action Normally"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]

        if logLine.pred == "PLAY" and len(logLine.items) == 1:
            target = logLine.items[0]
            cardInfo = getCardInfo(target)
            state.logLine += 1

            if state.actions > 0 and cardInfo.hasType(Types.ACTION):
                if state.moveCards([target], PlayerZones.HAND, PlayerZones.PLAY):
                    state.actions -= 1
                    state.candidates = [onPlay(target)]
                    return state
        return None


class buyPhaseA(Action):
    name = "Buy Phase A"

    def act(self, state, log):
        state = deepcopy(state)
        state.player = log[state.logLine].player
        state.stack = [buyPhaseA()]
        state.candidates = [
            buyPhaseB(),
            # repayDebt(), spendCoffers(),
            treasurePlayNormal(),
        ]
        return state


class treasurePlayNormal(Action):
    name = "Play Treasure(s) from Hand"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]

        if logLine.pred in ["PLAY", "PLAY_TREASURES_FOR"]:
            if state.moveCards(logLine.items, PlayerZones.HAND, PlayerZones.PLAY):

                for target in logLine.items:
                    if not getCardInfo(target).hasType(Types.TREASURE):
                        return None
                    state.stack.append(onPlay(target))
                state.logLine += 1
                state.candidates = [state.stack.pop()]
                return state
            else:
                return None
        else:
            return None


class buyPhaseB(Action):
    name = "Buy Phase B"

    def act(self, state, log):
        state = deepcopy(state)
        state.player = log[state.logLine].player
        state.stack = [buyPhaseB()]
        state.candidates = [nightPhase(), repayDebt(), buy()]
        return state


class repayDebt(Action):
    name = "Repay Debt"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]

        if logLine.pred == "REPAYS_DEBT":
            state.candidates = [state.stack.pop()]
            amount = int(logLine.args[1])

            if state.coins < amount:
                return None
            state.coins -= amount
            state.debt[state.player] -= amount
            return state

        elif logLine.pred == "REPAYS_SOME_DEBT":
            state.candidates = [state.stack.pop()]
            amount = int(logLine.args[0])

            if state.coins < amount:
                return None
            state.coins -= amount
            state.debt[state.player] -= amount
            return state

        else:
            return None


class nightPhase(Action):
    name = "Night Phase"

    def act(self, state, log):
        state = deepcopy(state)
        state.player = log[state.logLine].player
        state.stack = [nightPhase()]
        state.candidates = [cleanupPhase(), nightPlayNormal()]
        return state


class nightPlayNormal(Action):
    name = "Play Night from Hand"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]

        if logLine.pred == "PLAY" and len(logLine.items) == 1:
            target = logLine.items[0]
            cardInfo = getCardInfo(target)
            state.logLine += 1

            if cardInfo.hasType(Types.NIGHT) and state.zoneContains(
                target, PlayerZones.HAND
            ):
                state.moveCards([target], PlayerZones.HAND, PlayerZones.PLAY)
                state.candidates = [onPlay(target)]
                return state
            else:
                return None
        else:
            return None


class cleanupPhase(Action):
    name = "Cleanup Phase"

    def act(self, state, log):
        state = deepcopy(state)
        state.player = log[state.logLine].player
        state.stack = [cleanupPhase()]
        state.candidates = [cleanupDraw()] + state.cleanupEffects
        return state


class cleanupDraw(Action):
    name = "Cleanup Draw"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player
        # Discarding stuff from play / hands
        if not state.moveAllCards(PlayerZones.HAND, PlayerZones.DISCARD):
            return None

        toMove = copy([s[0] for s in state.stayOuts])
        toKeep = []
        for card in state.zones[PlayerZones.PLAY][state.player]:
            if card in toMove:
                toMove.remove(card)
                toKeep.append(card)

        if not state.moveAllCards(PlayerZones.PLAY, PlayerZones.DISCARD):
            return None
        state.moveCards(toKeep, PlayerZones.DISCARD, PlayerZones.PLAY)

        for s in state.stayOuts:
            s[1] -= 1
            if s[1] == 0:
                state.stayOuts.remove(s)

        state.stack = [newTurn()]
        state.candidates = [drawN(5)]
        return state


class play(Action):
    def __init__(self, src=PlayerZones.HAND):
        self.name = "Play from {}".format(src)
        self.src = src

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player

        if logLine.pred == "PLAY" and len(logLine.items) == 1:
            target = logLine.items[0]
            state.logLine += 1

            if state.moveCards([target], src, PlayerZones.PLAY):
                state.stack += [onPlay(target)]
                return state
        return None


class replay(Action):
    name = "Replay"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]

        if logLine.pred in ["PLAY", "PLAY_AGAIN", "PLAY_THIRD", "PLAY_AGAIN_CITADEL"]:
            target = logLine.items[0]
            state.logLine += 1

            state.candidates = [onPlay(target, False)]
            return state
        else:
            return None


class onPlay(Action):
    def __init__(self, target, realPlay=True):
        self.name = "On Play {}".format(target)
        self.target = target
        self.realPlay = realPlay  # For duration tracking purposes

    def act(self, state, log):
        state = deepcopy(state)
        cardInfo = getCardInfo(self.target)
        if hasattr(cardInfo, "onPlay"):
            return cardInfo.onPlay(state, log, self.realPlay)
        else:
            state.candidates = [state.stack.pop()]
            return state


class buy(Action):
    def __init__(self, src=NeutralZones.SUPPLY, dest=None):
        self.name = "Buy from {} to {}".format(src, dest)
        self.src = src
        self.dest = dest

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player

        if logLine.pred == "BUY_AND_GAIN":
            state.logLine += 1
            for target in logLine.items:
                cardInfo = getCardInfo(target)
                dest = self.dest if self.dest else cardInfo.gainDestination
                if not state.moveCards([target], self.src, dest):
                    return None

                state.stack += [onGain(target), onBuy(target)]

            state.candidates = [state.stack.pop()]
            return state

        elif logLine.pred == "BUY":
            state.logLine += 1
            for target in logLine.items:
                state.stack += [gain(self.src, self.dest), onBuy(target)]

            state.candidates = [state.stack.pop()]
            return state

        return None


class onBuy(Action):
    def __init__(self, target):
        self.name = "On Buy {}".format(target)
        self.target = target

    def act(self, state, log):
        state = deepcopy(state)
        cardInfo = getCardInfo(self.target)
        if hasattr(cardInfo, "onBuy"):
            return cardInfo.onBuy(state, log)
        else:
            state.candidates = [state.stack.pop()]
            return state


class gain(Action):
    def __init__(self, src=NeutralZones.SUPPLY, dest=None):
        self.name = "Gain from {} to {}".format(src, dest)
        self.src = src
        self.dest = dest

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player

        if logLine.pred == "GAIN":
            state.logLine += 1
            for target in logLine.items:
                cardInfo = getCardInfo(target)
                dest = self.dest if self.dest else cardInfo.gainDestination
                if not state.moveCards([target], self.src, dest):
                    return None

                state.stack.append(onGain(target))

            state.candidates = [state.stack.pop()]
            return state
        return None


class onGain(Action):
    def __init__(self, target):
        self.name = "On Gain {}".format(target)
        self.target = target

    def act(self, state, log):
        state = deepcopy(state)
        cardInfo = getCardInfo(self.target)
        if hasattr(cardInfo, "onGain"):
            return cardInfo.onGain(state, log)
        else:
            state.candidates = [state.stack.pop()]
            return state


class discard(Action):
    def __init__(self, src=PlayerZones.HAND, dest=PlayerZones.DISCARD):
        self.name = "Discard from {} to {}".format(src, dest)
        self.src = src
        self.dest = dest

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player

        if logLine.pred == "DISCARD":
            state.logLine += 1
            if not state.moveCards(logLine.items, self.src, self.dest):
                return None
            else:
                state.stack += [onDiscard(target) for target in logLine.items]

                state.candidates = [state.stack.pop()]
                return state
        return None


class onDiscard(Action):
    def __init__(self, target):
        self.name = "On Discard {}".format(target)
        self.target = target

    def act(self, state, log):
        state = deepcopy(state)
        cardInfo = getCardInfo(self.target)
        if hasattr(cardInfo, "onDiscard"):
            return cardInfo.onDiscard(state, log)
        else:
            state.candidates = [state.stack.pop()]
            return state


class trash(Action):
    def __init__(self, src=PlayerZones.HAND, dest=NeutralZones.TRASH):
        self.name = "Trash from {} to {}".format(src, dest)
        self.src = src
        self.dest = dest

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player

        if logLine.pred == "TRASH":
            state.logLine += 1
            if not state.moveCards(logLine.items, self.src, self.dest):
                return None
            else:
                state.stack += [onTrash(target) for target in logLine.items]

                state.candidates = [state.stack.pop()]
                return state
        return None


class onTrash(Action):
    def __init__(self, target):
        self.name = "On Trash {}".format(target)
        self.target = target

    def act(self, state, log):
        state = deepcopy(state)
        cardInfo = getCardInfo(self.target)
        if hasattr(cardInfo, "onTrash"):
            return cardInfo.onTrash(state, log)
        else:
            state.candidates = [state.stack.pop()]
            return state


class topdeck(Action):
    def __init__(self, src=PlayerZones.HAND, dest=PlayerZones.DECK):
        self.name = "Topdeck from {} to {}".format(src, dest)
        self.src = src
        self.dest = dest

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player

        if logLine.pred in ["TOPDECK", "INSERT_IN_DECK", "BOTTOMDECKS"]:
            state.logLine += 1
            if not state.moveCards(logLine.items, self.src, self.dest):
                return None
            else:
                state.stack += [onTopdeck(target) for target in logLine.items]

                state.candidates = [state.stack.pop()]
                return state
        return None


class onTopdeck(Action):
    def __init__(self, target):
        self.name = "On Topdeck {}".format(target)
        self.target = target

    def act(self, state, log):
        state = deepcopy(state)
        cardInfo = getCardInfo(self.target)
        if hasattr(cardInfo, "onTopdeck"):
            return cardInfo.onTopdeck(state, log)
        else:
            state.candidates = [state.stack.pop()]
            return state


class setAside(Action):
    def __init__(self, src=PlayerZones.HAND, dest=PlayerZones.SET_ASIDE):
        self.name = "Set Aside from {} to {}".format(src, dest)
        self.src = src
        self.dest = dest

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player

        if logLine.pred in ["SET_ASIDE", "SET_ASIDE_WITH"]:
            state.logLine += 1
            if state.moveCards(logLine.items, self.src, self.dest):
                state.candidates = [state.stack.pop()]
                return state
        return None


class revealHand(Action):
    name = "Reveal Hand"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player

        if logLine.pred == "REVEAL":
            state.logLine += 1
            if state.moveCards(logLine.items, PlayerZones.HAND, PlayerZones.HAND):
                state.candidates = [state.stack.pop()]
                return state
        return None


class putInHand(Action):
    name = "Put In Hand"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player

        if logLine.pred == "PUT_IN_HAND":
            state.logLine += 1
            if state.moveCards(logLine.items, PlayerZones.DECK, PlayerZones.HAND):
                state.candidates = [state.stack.pop()]
                return state
        return None


class getAction(Action):
    name = "Get Actions"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]

        if logLine.pred in ["GETS_ACTIONS", "GETS_ACTIONS_FROM"]:
            amount = int(logLine.args[0])
            state.actions += amount
            state.logLine += 1
            state.candidates = [state.stack.pop()]
            return state
        elif logLine.pred in ["GETS_ACTION", "GETS_ACTION_FROM"]:
            state.actions += 1
            state.logLine += 1
            state.candidates = [state.stack.pop()]
            return state
        else:
            return None


class getBuy(Action):
    name = "Get Buys"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]

        if logLine.pred in ["GETS_BUYS", "GETS_BUYS_FROM"]:
            amount = int(logLine.args[0])
            state.buys += amount
            state.logLine += 1
            state.candidates = [state.stack.pop()]
            return state
        elif logLine.pred in ["GETS_BUY", "GETS_BUY_FROM"]:
            state.buys += 1
            state.logLine += 1
            state.candidates = [state.stack.pop()]
            return state
        else:
            return None


class getCoin(Action):
    name = "Get Coins"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]

        if logLine.pred in ["GETS_COINS", "GETS_COINS_FROM"]:
            amount = int(logLine.args[0])
            state.coins += amount
            state.logLine += 1
            state.candidates = [state.stack.pop()]
            return state
        elif logLine.pred in ["GETS_COIN", "GETS_COIN_FROM"]:
            state.coins += 1
            state.logLine += 1
            state.candidates = [state.stack.pop()]
            return state
        else:
            return None


class takeDebt(Action):
    name = "Take Debt"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]

        if logLine.pred in ["TAX_TAKE_DEBT", "TAKES_DEBT"]:
            amount = int(logLine.args[0])
            state.debt[state.player] += amount
            state.logLine += 1
            state.candidates = [state.stack.pop()]
            return state
        else:
            return None


class lookAt(Action):
    name = "Look At"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]

        if logLine.pred == "LOOK_AT":
            state.logLine += 1
            state.candidates = [state.stack.pop()]
            return state
        else:
            return None


class lookAtN(Action):
    name = "Look At N"

    def __init__(self, n):
        self.n = n
        self.name = "Look At {}".format(n)

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player
        deckCount = state.zoneCount(PlayerZones.DECK)
        discardCount = state.zoneCount(PlayerZones.DISCARD)

        if deckCount < self.n and discardCount > 0:
            # Shuffle then go again
            state.candidates = [shuffle()]
            state.stack += [self]
            return state
        elif deckCount > 0:
            if log[state.logLine].pred == "LOOK_AT":
                state.logLine += 1
                if not state.moveCards(
                    logLine.items, PlayerZones.DECK, PlayerZones.DECK
                ):
                    return None
            else:
                return None
        state.candidates = [state.stack.pop()]
        return state


class reactToAttack(Action):
    name = "React to Attack"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]

        if logLine.pred == "REACTS_WITH":
            state.logLine += 1
            state.stack += [self]
            state.stack += [onReact(target) for target in logLine.items]

        state.candidates = [state.stack.pop()]
        return state


class onReact(Action):
    def __init__(self, target):
        self.name = "On React {}".format(target)
        self.target = target

    def act(self, state, log):
        state = deepcopy(state)
        cardInfo = getCardInfo(self.target)
        if hasattr(cardInfo, "onReact"):
            return cardInfo.onReact(state, log)
        else:
            state.candidates = [state.stack.pop()]
            return state


class passCard(Action):
    name = "Pass"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player

        if logLine.pred == "PASS":
            state.logLine += 1
            target = logLine.items[0]
            nextPlayer = (state.player + 1) % PLAYER_COUNT

            if not state.moveCards(
                [target], PlayerZones.HAND, PlayerZones.HAND, state.player, nextPlayer
            ):
                return None

            state.candidates = [state.stack.pop()]
            return state
        return None


class wishRight(Action):
    name = "Wish Success"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player

        if logLine.pred == "WISH_CORRECT":
            state.logLine += 1
            if not state.moveCards(
                [logLine.args[0]], PlayerZones.DECK, PlayerZones.HAND
            ):
                return None
            else:
                state.candidates = [state.stack.pop()]
                return state
        return None


class wishWrong(Action):
    name = "Wish Wrong"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player

        if logLine.pred == "WISH_WRONG":
            state.logLine += 1
            if not state.moveCards(
                [logLine.args[1]], PlayerZones.DECK, PlayerZones.DECK
            ):
                return None
            else:
                state.candidates = [state.stack.pop()]
                return state
        return None


class returnCard(Action):
    name = "Return"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player

        if logLine.pred in ["RETURN", "RETURN TO"]:
            state.logLine += 1
            if not state.moveCards(
                logLine.items, PlayerZones.HAND, NeutralZones.SUPPLY
            ):
                return None

            state.candidates = [state.stack.pop()]
            return state
        return None


class forceEnd(Action):
    name = "Win"

    def act(self, state, log):
        state = deepcopy(state)
        state.logLine += 900
        state.candidates = [forceEnd()]
        return state


# ## Cards and related actions ## #


class CardInfo:
    names = ["Back", "Backs", "a Back"]
    types = []
    cost = [0, 0, 0]
    isOrderedPile = False
    initialZone = NeutralZones.SUPPLY
    gainDestination = PlayerZones.DISCARD

    def hasType(self, cardType):
        return cardType in self.types

    def getKeyCard(self):
        if hasattr(self, "keyCard"):
            return self.keyCard
        else:
            return self.names[0]

    def getPileCards(self):
        if hasattr(self, "pileCard"):
            return self.pileCards
        else:
            return [self.names[0]]

    def onBuy(self, state, log):
        state = deepcopy(state)
        state.coins -= max(0, self.cost[0] - state.reductions)
        state.potions -= self.cost[1]
        state.buys -= 1
        if self.cost[2] > 0:
            state.stack.append(takeDebt())
        if state.coins >= 0 and state.potions >= 0 and state.buys >= 0:
            state.candidates = [state.stack.pop()]
            return state


class CURSE(CardInfo):
    names = ["Curse", "Curses", "a Curse"]
    types = [Types.CURSE]
    cost = [0, 0, 0]


class COPPER(CardInfo):
    names = ["Copper", "Coppers", "a Copper"]
    types = [Types.TREASURE]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.candidates = [state.stack.pop()]
        state.coins += 1
        return state


class SILVER(CardInfo):
    names = ["Silver", "Silvers", "a Silver"]
    types = [Types.TREASURE]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.candidates = [state.stack.pop()]
        state.coins += 2
        return state


class GOLD(CardInfo):
    names = ["Gold", "Golds", "a Gold"]
    types = [Types.TREASURE]
    cost = [6, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.candidates = [state.stack.pop()]
        state.coins += 3
        return state


class ESTATE(CardInfo):
    names = ["Estate", "Estates", "an Estate"]
    types = [Types.VICTORY]
    cost = [2, 0, 0]


class DUCHY(CardInfo):
    names = ["Duchy", "Duchies", "a Duchy"]
    types = [Types.VICTORY]
    cost = [5, 0, 0]


class PROVINCE(CardInfo):
    names = ["Province", "Provinces", "a Province"]
    types = [Types.VICTORY]
    cost = [8, 0, 0]


class ARTISAN(CardInfo):
    names = ["Artisan", "Artisans", "an Artisan"]
    types = [Types.ACTION]
    cost = [6, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [
            hasCards(topdeck()),
            maybe(gain(NeutralZones.SUPPLY, PlayerZones.HAND)),
        ]
        state.candidates = [state.stack.pop()]
        return state


class BANDIT(CardInfo):
    names = ["Bandit", "Bandits", "a Bandit"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [
            maybe(discard(PlayerZones.DECK, PlayerZones.DISCARD)),
            maybe(trash(PlayerZones.DECK, NeutralZones.TRASH)),
            maybe(revealN(2)),
            maybe(gain()),
            reactToAttack(),
        ]
        state.candidates = [state.stack.pop()]
        return state


class BUREAUCRAT(CardInfo):
    names = ["Bureaucrat", "Bureaucrats", "a Bureaucrat"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [
            maybe(topdeck()),
            maybe(revealHand()),
            maybe(gain(NeutralZones.SUPPLY, PlayerZones.DECK)),
            reactToAttack(),
        ]
        state.candidates = [state.stack.pop()]
        return state


class CELLAR(CardInfo):
    names = ["Cellar", "Cellars", "a Cellar"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        if state.logLine < len(log) - 1:
            amount = len(log[state.logLine + 1].items)
        state.stack += [maybe(drawN(amount)), maybe(discard()), getAction()]
        state.candidates = [state.stack.pop()]
        return state


class CHAPEL(CardInfo):
    names = ["Chapel", "Chapels", "a Chapel"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [maybe(trash())]
        state.candidates = [state.stack.pop()]
        return state


class COUNCIL_ROOM(CardInfo):
    names = ["Council Room", "Council Rooms", "a Council Room"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        logLine = log[state.logLine]
        for p in range(PLAYER_COUNT):
            if p != logLine.player:
                state.stack += [drawN(1, p)]
        state.stack += [getBuy(), drawN(4)]
        state.candidates = [state.stack.pop()]
        return state


class FESTIVAL(CardInfo):
    names = ["Festival", "Festivals", "a Festival"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [getCoin(), getBuy(), getAction()]
        state.candidates = [state.stack.pop()]
        return state


class GARDENS(CardInfo):
    names = ["Gardens", "Gardens", "a Gardens"]
    types = [Types.VICTORY]
    cost = [4, 0, 0]


class HARBINGER(CardInfo):
    names = ["Harbinger", "Harbingers", "a Harbinger"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        # For some reason harbinger looks at discard twice
        state.stack += [
            maybe(topdeck(PlayerZones.DISCARD, PlayerZones.DECK)),
            maybe(lookAt()),
            maybe(lookAt()),
            getAction(),
            drawN(1),
        ]
        state.candidates = [state.stack.pop()]
        return state


class LABORATORY(CardInfo):
    names = ["Laboratory", "Laboratories", "a Laboratory"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [getAction(), drawN(2)]
        state.candidates = [state.stack.pop()]
        return state


class LIBRARY(CardInfo):
    names = ["Library", "Libraries", "a Library"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player

        handCount = state.zoneCount(PlayerZones.HAND)
        deckCount = state.zoneCount(PlayerZones.DECK) + state.zoneCount(
            PlayerZones.DISCARD
        )

        if handCount >= 7 or deckCount == 0:
            state.candidates = [
                maybe(discard(PlayerZones.SET_ASIDE, PlayerZones.DISCARD))
            ]
        else:
            state.stack += [
                onPlay("Library"),
                maybe(setAside()),
                maybe(lookAt()),
                drawN(1),
            ]
            state.candidates = [state.stack.pop()]

        return state


class MARKET(CardInfo):
    names = ["Market", "Markets", "a Market"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [getCoin(), getBuy(), getAction(), drawN(1)]
        state.candidates = [state.stack.pop()]
        return state


class MERCHANT(CardInfo):
    names = ["Merchant", "Merchants", "a Merchant"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [getAction(), drawN(1)]
        state.candidates = [state.stack.pop()]
        return state


class MILITIA(CardInfo):
    names = ["Militia", "Militias", "a Militia"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [maybe(discard()), getCoin(), reactToAttack()]
        state.candidates = [state.stack.pop()]
        return state


class MINE(CardInfo):
    names = ["Mine", "Mines", "a Mine"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [gain(NeutralZones.SUPPLY, PlayerZones.HAND), trash()]
        state.candidates = [state.stack.pop()]
        return state


class MOAT(CardInfo):
    # The reaction aspect of moat is baked into every attack -
    # The 'attack' parts are all maybe-d.
    names = ["Moat", "Moats", "a Moat"]
    types = [Types.ACTION, Types.REACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [drawN(2)]
        state.candidates = [state.stack.pop()]
        return state

    def onReact(self, state, log):
        state = deepcopy(state)
        state.candidates = [state.stack.pop()]
        return state


class MONEYLENDER(CardInfo):
    names = ["Moneylender", "Moneylenders", "a Moneylender"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [maybe(getCoin()), maybe(trash())]
        state.candidates = [state.stack.pop()]
        return state


class POACHER(CardInfo):
    names = ["Poacher", "Poachers", "a Poacher"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [maybe(discard()), getCoin(), getAction(), drawN(1)]
        state.candidates = [state.stack.pop()]
        return state


class REMODEL(CardInfo):
    names = ["Remodel", "Remodels", "a Remodel"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [gain(), trash()]
        state.candidates = [state.stack.pop()]
        return state


class SENTRY(CardInfo):
    names = ["Sentry", "Sentries", "a Sentry"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [
            maybe(topdeck(PlayerZones.DECK, PlayerZones.DECK)),
            maybe(discard(PlayerZones.DECK, PlayerZones.DISCARD)),
            maybe(trash(PlayerZones.DECK, NeutralZones.TRASH)),
            maybe(lookAtN(2)),
            getAction(),
            drawN(1),
        ]
        state.candidates = [state.stack.pop()]
        return state


class SMITHY(CardInfo):
    names = ["Smithy", "Smithies", "a Smithy"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [drawN(3)]
        state.candidates = [state.stack.pop()]
        return state


class THRONE_ROOM(CardInfo):
    names = ["Throne Room", "Throne Rooms", "a Throne Room"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [replay(), play()]
        state.candidates = [state.stack.pop()]
        return state


class VASSAL(CardInfo):
    names = ["Vassal", "Vassals", "a Vassal"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [
            maybe(play(PlayerZones.DISCARD)),
            maybe(discard(PlayerZones.DECK, PlayerZones.DISCARD)),
            getCoin(),
        ]
        state.candidates = [state.stack.pop()]
        return state


class VILLAGE(CardInfo):
    names = ["Village", "Villages", "a Village"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [getAction(), drawN(1)]
        state.candidates = [state.stack.pop()]
        return state


class WITCH(CardInfo):
    names = ["Witch", "Witches", "a Witch"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [maybe(gain()), drawN(2, state.player), reactToAttack()]
        state.candidates = [state.stack.pop()]
        return state


class WORKSHOP(CardInfo):
    names = ["Workshop", "Workshops", "a Workshop"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [maybe(gain())]
        state.candidates = [state.stack.pop()]
        return state


class COURTYARD(CardInfo):
    names = ["Couryard", "Courtyards", "a Courtyard"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [hasCards(topdeck()), drawN(3)]
        state.candidates = [state.stack.pop()]
        return state


class CONSPIRATOR(CardInfo):
    names = ["Conspirator", "Conspirators", "a Conspirator"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [maybe(getAction()), maybe(drawN(1)), getCoin()]
        state.candidates = [state.stack.pop()]
        return state


class COURTIER(CardInfo):
    names = ["Courtier", "Courtiers", "a Courtier"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [
            maybe(gain()),
            maybe(getCoin()),
            maybe(getBuy()),
            maybe(getAction()),
            revealHand(),
        ]
        state.candidates = [state.stack.pop()]
        return state


class BARON(CardInfo):
    names = ["Baron", "Barons", "a Baron"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [
            maybe(gain()),
            maybe(getCoin()),
            maybe(getBuy()),
            maybe(discard()),
        ]
        state.candidates = [state.stack.pop()]
        return state


class BRIDGE(CardInfo):
    names = ["Bridge", "Bridges", "a Bridge"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.reductions += 1
        state.stack += [getCoin(), getBuy()]
        state.candidates = [state.stack.pop()]
        return state


class DIPLOMAT(CardInfo):
    names = ["Diplomat", "Diplomats", "a Diplomat"]
    types = [Types.ACTION, Types.REACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [maybe(getAction()), drawN(2)]
        state.candidates = [state.stack.pop()]
        return state

    def onReact(self, state, log):
        state = deepcopy(state)
        state.stack += [hasCards(discard()), drawN(2)]
        state.candidates = [state.stack.pop()]
        return state


class DUKE(CardInfo):
    names = ["Duke", "Dukes", "a Duke"]
    types = [Types.VICTORY]
    cost = [5, 0, 0]


class HAREM(CardInfo):
    names = ["Harem", "Harems", "a Harem"]
    types = [Types.TREASURE, Types.VICTORY]
    cost = [6, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.candidates = [state.stack.pop()]
        state.coins += 2
        return state


class NOBLES(CardInfo):
    names = ["Nobles", "Nobles", "a Nobles"]
    types = [Types.ACTION, Types.VICTORY]
    cost = [6, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.candidates = [getAction(), drawN(3)]
        return state


class IRONWORKS(CardInfo):
    names = ["Ironworks", "Ironworks", "an Ironworks"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [
            maybe(drawN(1)),
            maybe(getCoin()),
            maybe(getAction()),
            maybe(gain()),
        ]
        state.candidates = [state.stack.pop()]
        return state


class LURKER(CardInfo):
    names = ["Lurker", "Lurkers", "a Lurker"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [
            maybe(trash(NeutralZones.SUPPLY, NeutralZones.TRASH)),
            maybe(gain(NeutralZones.TRASH, None)),
        ]
        state.candidates = [state.stack.pop()]
        return state


class MASQUERADE(CardInfo):
    names = ["Masquerade", "Masquerades", "a Masquerade"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [maybe(trash())]
        state.stack += [maybe(passCard()) for p in range(PLAYER_COUNT)]
        state.stack.append(drawN(2))
        state.candidates = [state.stack.pop()]
        return state


class MILL(CardInfo):
    names = ["Mill", "Mills", "a Mill"]
    types = [Types.ACTION, Types.VICTORY]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [maybe(getCoin()), maybe(discard()), getActions(), drawN(1)]
        state.candidates = [state.stack.pop()]
        return state


class MINING_VILLAGE(CardInfo):
    names = ["Mining Village", "Mining Villages", "a Mining Village"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [
            maybe(getCoin()),
            maybe(trash(PlayerZones.PLAY, NeutralZones.TRASH)),
            getActions(),
            drawN(1),
        ]
        state.candidates = [state.stack.pop()]
        return state


class MINION(CardInfo):
    names = ["Minion", "Minions", "a Minion"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        for p in range(PLAYER_COUNT):
            state.stack += [maybe(drawN(4)), maybe(discard())]
        state.stack += [maybe(getCoin()), getAction(), reactToAttack()]
        state.candidates = [state.stack.pop()]
        return state


class PATROL(CardInfo):
    names = ["Patrol", "Patrols", "a Patrol"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [
            maybe(topdeck(PlayerZones.DECK, PlayerZones.DECK)),
            maybe(putInHand()),
            revealN(4),
            drawN(3),
        ]
        state.candidates = [state.stack.pop()]
        return state


class PAWN(CardInfo):
    names = ["Pawn", "Pawns", "a Pawn"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [
            maybe(getCoin()),
            maybe(getBuy()),
            maybe(getAction()),
            maybe(drawN(1)),
        ]
        state.candidates = [state.stack.pop()]
        return state


class replaceGain(Action):
    name = "Replace Gain"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player

        if logLine.pred == "GAIN":
            state.logLine += 1
            if len(logLine.items) == 1:
                target = logLine.items[0]
                cardInfo = getCardInfo(target)
                dest = cardInfo.gainDestination

                if cardInfo.hasType(Type.TREASURE) or cardInfo.hasType(Type.ACTION):
                    dest = PlayerZones.DECK
                if cardInfo.hasType(Type.VICTORY):
                    state.stack.append(gain())
                if not state.moveCards([target], self.src, dest):
                    return None

                state.stack.append(onGain(target))

                state.candidates = [state.stack.pop()]
                return state
        return None


class REPLACE(CardInfo):
    names = ["Replace", "Replaces", "a Replace"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [maybe(replaceGain()), hasCards(trash()), reactToAttack()]
        state.candidates = [state.stack.pop()]
        return state


class SECRET_PASSAGE(CardInfo):
    names = ["Secret Passage", "Secret Passages", "a Secret Passage"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [hasCards(topdeck()), getAction(), drawN(2)]
        state.candidates = [state.stack.pop()]
        return state


class SHANTY_TOWN(CardInfo):
    names = ["Shanty Town", "Shanty Towns", "a Shanty Town"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [maybe(drawN(2)), revealHand(), getAction()]
        state.candidates = [state.stack.pop()]
        return state


class STEWARD(CardInfo):
    names = ["Steward", "Stewards", "a Steward"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.candidates = [drawN(2), trash(), getCoin()]
        return state


class SWINDLER(CardInfo):
    names = ["Swindler", "Swindlers", "a Swindler"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [
            maybe(gain()),
            maybe(trash(PlayerZones.DECK, NeutralZones.TRASH)),
            getCoin(),
            reactToAttack(),
        ]
        state.candidates = [state.stack.pop()]
        return state


class TORTURER(CardInfo):
    names = ["Torturer", "Torturers", "a Torturer"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [
            maybe(discard()),
            maybe(gain(NeutralZones.SUPPLY, PlayerZones.HAND)),
            drawN(5),
            reactToAttack(),
        ]
        state.candidates = [state.stack.pop()]
        return state


class TRADING_POST(CardInfo):
    names = ["Trading Post", "Trading Posts", "a Trading Post"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [
            maybe(gain(NeutralZones.SUPPLY, PlayerZones.HAND)),
            hasCards(trash()),
        ]
        state.candidates = [state.stack.pop()]
        return state


class UPGRADE(CardInfo):
    names = ["Upgrade", "Upgrades", "an Upgrade"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [maybe(gain()), hasCards(trash()), getAction(), drawN(1)]
        state.candidates = [state.stack.pop()]
        return state


class WISHING_WELL(CardInfo):
    names = ["Wishing Well", "Wishing Wells", "a Wishing Well"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [maybe(wishWrong()), maybe(wishRight()), getAction(), drawN(1)]
        state.candidates = [state.stack.pop()]
        return state


class AMBASSADOR(CardInfo):
    names = ["Ambassador", "Ambassadors", "a Ambassador"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [maybe(gain()), maybe(returnCards()), hasCards(revealHand())]
        state.candidates = [state.stack.pop()]


class BAZAAR(CardInfo):
    names = ["Bazaar", "Bazaars", "a Bazaar"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += [getCoin(), getAction(), drawN(1)]
        state.candidates = [state.stack.pop()]
        return state


class CARAVAN(CardInfo):
    names = ["Caravan", "Caravans", "a Caravan"]
    types = [Types.ACTION, Types.DURATION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        if realPlay:
            state.stayOuts.append(["Caravan", 1])
        state.turnStarts.append(["Caravan"])
        state.stack += [getAction(), drawN(1)]
        state.candidates = [state.stack.pop()]
        return state

    def onDuration(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]

        deckCount = state.zoneCount(PlayerZones.DECK)
        discardCount = state.zoneCount(PlayerZones.DISCARD)
        if deckCount == 0 and discardCount > 0:
            # Shuffle then go again
            state.candidates = [shuffle()]
            state.stack += [self]
            return state
        elif logLine.pred == "DRAW_FROM_CARAVAN":
            amount = len(logLine.items)
            state.logLine += 1
            if not state.moveCards(logLine.items, PlayerZones.DECK, PlayerZones.HAND):
                return None

            i = 0
            remaining = []
            for d in state.turnStarts:
                if d[0] == "Caravan" and i < amount:
                    i += 1
                else:
                    remaining.append(d)

            if i < amount:
                return None
            else:
                state.candidates = [state.stack.pop()]
                return state
        else:
            return None


class CUTPURSE(CardInfo):
    names = ["Cutpurse", "Cutpurses", "a Cutpurse"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class EMBARGO(CardInfo):
    names = ["Embargo", "Embargos", "an Embargo"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class EXPLORER(CardInfo):
    names = ["Explorer", "Explorers", "an Explorer"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class FISHING_VILLAGE(CardInfo):
    names = ["Fishing Village", "Fishing Villages", "a Fishing Village"]
    types = [Types.ACTION, Types.DURATION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class GHOST_SHIP(CardInfo):
    names = ["Ghost Ship", "Ghost Ships", "a Ghost Ship"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class HAVEN(CardInfo):
    names = ["Haven", "Havens", "a Haven"]
    types = [Types.ACTION, Types.DURATION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ISLAND(CardInfo):
    names = ["Island", "Islands", "an Island"]
    types = [Types.ACTION, Types.VICTORY]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class LIGHTHOUSE(CardInfo):
    names = ["Lighthouse", "Lighthouses", "a Lighthouse"]
    types = [Types.ACTION, Types.DURATION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class LOOKOUT(CardInfo):
    names = ["Lookout", "Lookouts", "a Lookout"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class MERCHANT_SHIP(CardInfo):
    names = ["Merchant Ship", "Merchant Ships", "a Merchant Ship"]
    types = [Types.ACTION, Types.DURATION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class NATIVE_VILLAGE(CardInfo):
    names = ["Native Village", "Native Villages", "a Native Village"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class NAVIGATOR(CardInfo):
    names = ["Navigator", "Navigators", "a Navigator"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class OUTPOST(CardInfo):
    names = ["Outpost", "Outposts", "an Outpost"]
    types = [Types.ACTION, Types.DURATION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class PEARL_DIVER(CardInfo):
    names = ["Pearl Diver", "Pearl Divers", "a Pearl Diver"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class PIRATE_SHIP(CardInfo):
    names = ["Pirate Ship", "Pirate Ships", "a Pirate Ship"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SALVAGER(CardInfo):
    names = ["Salvager", "Salvagers", "a Salvager"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SEA_HAG(CardInfo):
    names = ["Sea Hag", "Sea Hags", "a Sea Hag"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SMUGGLERS(CardInfo):
    names = ["Smugglers", "Smugglers", "a Smugglers"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TACTICIAN(CardInfo):
    names = ["Tactician", "Tacticians", "a Tactician"]
    types = [Types.ACTION, Types.DURATION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TREASURE_MAP(CardInfo):
    names = ["Treasure Map", "Treasure Maps", "a Treasure Map"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TREASURY(CardInfo):
    names = ["Treasury", "Treasuries", "a Treasury"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WAREHOUSE(CardInfo):
    names = ["Warehouse", "Warehouses", "a Warehouse"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WHARF(CardInfo):
    names = ["Wharf", "Wharves", "a Wharf"]
    types = [Types.ACTION, Types.DURATION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ALCHEMIST(CardInfo):
    names = ["Alchemist", "Alchemists", "an Alchemist"]
    types = [Types.ACTION]
    cost = [3, 1, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class APOTHECARY(CardInfo):
    names = ["Apothecary", "Apothecaries", "an Apothecary"]
    types = [Types.ACTION]
    cost = [2, 1, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class APPRENTICE(CardInfo):
    names = ["Apprentice", "Apprentices", "an Apprentice"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class FAMILIAR(CardInfo):
    names = ["Familiar", "Familiars", "a Familiar"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [3, 1, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class GOLEM(CardInfo):
    names = ["Golem", "Golems", "a Golem"]
    types = [Types.ACTION]
    cost = [4, 1, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class HERBALIST(CardInfo):
    names = ["Herbalist", "Herbalists", "a Herbalist"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class PHILOSOPHERS_STONE(CardInfo):
    names = ["Philosopher's Stone", "Philosopher's Stones", "a Philosopher's Stone"]
    types = [Types.TREASURE]
    cost = [3, 1, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class POSSESSION(CardInfo):
    names = ["Possession", "Possessions", "a Possession"]
    types = [Types.ACTION]
    cost = [6, 1, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class POTION(CardInfo):
    names = ["Potion", "Potions", "a Potion"]
    types = [Types.TREASURE]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SCRYING_POOL(CardInfo):
    names = ["Scrying Pool", "Scrying Pools", "a Scrying Pool"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [2, 1, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TRANSMUTE(CardInfo):
    names = ["Transmute", "Transmutes", "a Transmute"]
    types = [Types.ACTION]
    cost = [0, 1, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class UNIVERSITY(CardInfo):
    names = ["University", "Universities", "a University"]
    types = [Types.ACTION]
    cost = [2, 1, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class VINEYARD(CardInfo):
    names = ["Vineyard", "Vineyards", "a Vineyard"]
    types = [Types.VICTORY]
    cost = [0, 1, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BANK(CardInfo):
    names = ["Bank", "Banks", "a Bank"]
    types = [Types.TREASURE]
    cost = [7, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BISHOP(CardInfo):
    names = ["Bishop", "Bishops", "a Bishop"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class COLONY(CardInfo):
    names = ["Colony", "Colonies", "a Colony"]
    types = [Types.VICTORY]
    cost = [11, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CONTRABAND(CardInfo):
    names = ["Contraband", "Contrabands", "a Contraband"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class COUNTING_HOUSE(CardInfo):
    names = ["Counting House", "Counting Houses", "a Counting House"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CITY(CardInfo):
    names = ["City", "Cities", "a City"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class EXPAND(CardInfo):
    names = ["Expand", "Expands", "an Expand"]
    types = [Types.ACTION]
    cost = [7, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class FORGE(CardInfo):
    names = ["Forge", "Forges", "a Forge"]
    types = [Types.ACTION]
    cost = [7, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class GRAND_MARKET(CardInfo):
    names = ["Grand Market", "Grand Markets", "a Grand Market"]
    types = [Types.ACTION]
    cost = [6, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class GOONS(CardInfo):
    names = ["Goons", "Goons", "a Goons"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [6, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class HOARD(CardInfo):
    names = ["Hoard", "Hoards", "a Hoard"]
    types = [Types.TREASURE]
    cost = [6, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class KINGS_COURT(CardInfo):
    names = ["King's Court", "King's Courts", "a King's Court"]
    types = [Types.ACTION]
    cost = [7, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class LOAN(CardInfo):
    names = ["Loan", "Loans", "a Loan"]
    types = [Types.TREASURE]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class MINT(CardInfo):
    names = ["Mint", "Mints", "a Mint"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class MONUMENT(CardInfo):
    names = ["Monument", "Monuments", "a Monument"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class MOUNTEBANK(CardInfo):
    names = ["Mountebank", "Mountebanks", "a Mountebank"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class PEDDLER(CardInfo):
    names = ["Peddler", "Peddlers", "a Peddler"]
    types = [Types.ACTION]
    cost = [8, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class PLATINUM(CardInfo):
    names = ["Platinum", "Platina", "a Platinum"]
    types = [Types.TREASURE]
    cost = [9, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class QUARRY(CardInfo):
    names = ["Quarry", "Quarries", "a Quarry"]
    types = [Types.TREASURE]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class RABBLE(CardInfo):
    names = ["Rabble", "Rabbles", "a Rabble"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ROYAL_SEAL(CardInfo):
    names = ["Royal Seal", "Royal Seals", "a Royal Seal"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TALISMAN(CardInfo):
    names = ["Talisman", "Talismans", "a Talisman"]
    types = [Types.TREASURE]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TRADE_ROUTE(CardInfo):
    names = ["Trade Route", "Trade Routes", "a Trade Route"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class VAULT(CardInfo):
    names = ["Vault", "Vaults", "a Vault"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class VENTURE(CardInfo):
    names = ["Venture", "Ventures", "a Venture"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WATCHTOWER(CardInfo):
    names = ["Watchtower", "Watchtowers", "a Watchtower"]
    types = [Types.ACTION, Types.REACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WORKERS_VILLAGE(CardInfo):
    names = ["Worker's Village", "Worker's Villages", "a Worker's Village"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class PRIZE(CardInfo):
    names = ["Prize", "Prize", "Prize"]
    types = []
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BAG_OF_GOLD(CardInfo):
    names = ["Bag of Gold", "Bags of Gold", "a Bag of Gold"]
    types = [Types.ACTION, Types.PRIZE]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DIADEM(CardInfo):
    names = ["Diadem", "Diadems", "a Diadem"]
    types = [Types.TREASURE, Types.PRIZE]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class FAIRGROUNDS(CardInfo):
    names = ["Fairgrounds", "Fairgrounds", "a Fairgrounds"]
    types = [Types.VICTORY]
    cost = [6, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class FARMING_VILLAGE(CardInfo):
    names = ["Farming Village", "Farming Villages", "a Farming Village"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class FOLLOWERS(CardInfo):
    names = ["Followers", "Followers", "a Followers"]
    types = [Types.ACTION, Types.ATTACK, Types.PRIZE]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class FORTUNE_TELLER(CardInfo):
    names = ["Fortune Teller", "Fortune Tellers", "a Fortune Teller"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class HAMLET(CardInfo):
    names = ["Hamlet", "Hamlets", "a Hamlet"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class HARVEST(CardInfo):
    names = ["Harvest", "Harvests", "a Harvest"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class HORSE_TRADERS(CardInfo):
    names = ["Horse Traders", "Horse Traders", "a Horse Traders"]
    types = [Types.ACTION, Types.REACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class HORN_OF_PLENTY(CardInfo):
    names = ["Horn of Plenty", "Horns of Plenty", "a Horn of Plenty"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class HUNTING_PARTY(CardInfo):
    names = ["Hunting Party", "Hunting Parties", "a Hunting Party"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class JESTER(CardInfo):
    names = ["Jester", "Jesters", "a Jester"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class MENAGERIE(CardInfo):
    names = ["Menagerie", "Menageries", "a Menagerie"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class PRINCESS(CardInfo):
    names = ["Princess", "Princesses", "a Princess"]
    types = [Types.ACTION, Types.PRIZE]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class REMAKE(CardInfo):
    names = ["Remake", "Remakes", "a Remake"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TOURNAMENT(CardInfo):
    names = ["Tournament", "Tournaments", "a Tournament"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TRUSTY_STEED(CardInfo):
    names = ["Trusty Steed", "Trusty Steeds", "a Trusty Steed"]
    types = [Types.ACTION, Types.PRIZE]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class YOUNG_WITCH(CardInfo):
    names = ["Young Witch", "Young Witches", "a Young Witch"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BORDER_VILLAGE(CardInfo):
    names = ["Border Village", "Border Villages", "a Border Village"]
    types = [Types.ACTION]
    cost = [6, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CACHE(CardInfo):
    names = ["Cache", "Caches", "a Cache"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CARTOGRAPHER(CardInfo):
    names = ["Cartographer", "Cartographers", "a Cartographer"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CROSSROADS(CardInfo):
    names = ["Crossroads", "Crossroads", "a Crossroads"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DEVELOP(CardInfo):
    names = ["Develop", "Develops", "a Develop"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DUCHESS(CardInfo):
    names = ["Duchess", "Duchesses", "a Duchess"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class EMBASSY(CardInfo):
    names = ["Embassy", "Embassies", "an Embassy"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class FARMLAND(CardInfo):
    names = ["Farmland", "Farmlands", "a Farmland"]
    types = [Types.VICTORY]
    cost = [6, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class FOOLS_GOLD(CardInfo):
    names = ["Fool's Gold", "Fool's Golds", "a Fool's Gold"]
    types = [Types.TREASURE, Types.REACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class HAGGLER(CardInfo):
    names = ["Haggler", "Hagglers", "a Haggler"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class HIGHWAY(CardInfo):
    names = ["Highway", "Highways", "a Highway"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ILL_GOTTEN_GAINS(CardInfo):
    names = ["Ill-Gotten Gains", "Ill-Gotten Gains", "an Ill-Gotten Gains"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class INN(CardInfo):
    names = ["Inn", "Inns", "an Inn"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class JACK_OF_ALL_TRADES(CardInfo):
    names = ["Jack of All Trades", "Jacks of All Trades", "a Jack of All Trades"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class MANDARIN(CardInfo):
    names = ["Mandarin", "Mandarins", "a Mandarin"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class NOBLE_BRIGAND(CardInfo):
    names = ["Noble Brigand", "Noble Brigands", "a Noble Brigand"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class NOMAD_CAMP(CardInfo):
    names = ["Nomad Camp", "Nomad Camps", "a Nomad Camp"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class OASIS(CardInfo):
    names = ["Oasis", "Oases", "an Oasis"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ORACLE(CardInfo):
    names = ["Oracle", "Oracles", "an Oracle"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class MARGRAVE(CardInfo):
    names = ["Margrave", "Margraves", "a Margrave"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SCHEME(CardInfo):
    names = ["Scheme", "Schemes", "a Scheme"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SILK_ROAD(CardInfo):
    names = ["Silk Road", "Silk Roads", "a Silk Road"]
    types = [Types.VICTORY]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SPICE_MERCHANT(CardInfo):
    names = ["Spice Merchant", "Spice Merchants", "a Spice Merchant"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class STABLES(CardInfo):
    names = ["Stables", "Stables", "a Stables"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TRADER(CardInfo):
    names = ["Trader", "Traders", "a Trader"]
    types = [Types.ACTION, Types.REACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TUNNEL(CardInfo):
    names = ["Tunnel", "Tunnels", "a Tunnel"]
    types = [Types.VICTORY, Types.REACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class RUINS(CardInfo):
    names = ["Ruins", "Ruins", "a Ruins"]
    types = [Types.ACTION, Types.RUINS]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class KNIGHTS(CardInfo):
    names = ["Knights", "Knights", "a Knights"]
    types = [Types.ACTION, Types.ATTACK, Types.KNIGHT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ABANDONED_MINE(CardInfo):
    names = ["Abandoned Mine", "Abandoned Mines", "an Abandoned Mine"]
    types = [Types.ACTION, Types.RUINS]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ALTAR(CardInfo):
    names = ["Altar", "Altars", "an Altar"]
    types = [Types.ACTION]
    cost = [6, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ARMORY(CardInfo):
    names = ["Armory", "Armories", "an Armory"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BAND_OF_MISFITS(CardInfo):
    names = ["Band of Misfits", "Bands of Misfits", "a Band of Misfits"]
    types = [Types.ACTION, Types.COMMAND]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BANDIT_CAMP(CardInfo):
    names = ["Bandit Camp", "Bandit Camps", "a Bandit Camp"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BEGGAR(CardInfo):
    names = ["Beggar", "Beggars", "a Beggar"]
    types = [Types.ACTION, Types.REACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CATACOMBS(CardInfo):
    names = ["Catacombs", "Catacombs", "a Catacombs"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class COUNT(CardInfo):
    names = ["Count", "Counts", "a Count"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class COUNTERFEIT(CardInfo):
    names = ["Counterfeit", "Counterfeits", "a Counterfeit"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CULTIST(CardInfo):
    names = ["Cultist", "Cultists", "a Cultist"]
    types = [Types.ACTION, Types.ATTACK, Types.LOOTER]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DAME_ANNA(CardInfo):
    names = ["Dame Anna", "Dame Annas", "Dame Anna"]
    types = [Types.ACTION, Types.ATTACK, Types.KNIGHT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DAME_JOSEPHINE(CardInfo):
    names = ["Dame Josephine", "Dame Josephines", "Dame Josephine"]
    types = [Types.ACTION, Types.ATTACK, Types.KNIGHT, Types.VICTORY]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DAME_MOLLY(CardInfo):
    names = ["Dame Molly", "Dame Mollies", "Dame Molly"]
    types = [Types.ACTION, Types.ATTACK, Types.KNIGHT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DAME_NATALIE(CardInfo):
    names = ["Dame Natalie", "Dame Natalies", "Dame Natalie"]
    types = [Types.ACTION, Types.ATTACK, Types.KNIGHT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DAME_SYLVIA(CardInfo):
    names = ["Dame Sylvia", "Dame Sylvias", "Dame Sylvia"]
    types = [Types.ACTION, Types.ATTACK, Types.KNIGHT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DEATH_CART(CardInfo):
    names = ["Death Cart", "Death Carts", "a Death Cart"]
    types = [Types.ACTION, Types.LOOTER]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class FEODUM(CardInfo):
    names = ["Feodum", "Feoda", "a Feodum"]
    types = [Types.VICTORY]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class FORAGER(CardInfo):
    names = ["Forager", "Foragers", "a Forager"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class FORTRESS(CardInfo):
    names = ["Fortress", "Fortresses", "a Fortress"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class GRAVEROBBER(CardInfo):
    names = ["Graverobber", "Graverobbers", "a Graverobber"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class HERMIT(CardInfo):
    names = ["Hermit", "Hermits", "a Hermit"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class HOVEL(CardInfo):
    names = ["Hovel", "Hovels", "a Hovel"]
    types = [Types.REACTION, Types.SHELTER]
    cost = [1, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class HUNTING_GROUNDS(CardInfo):
    names = ["Hunting Grounds", "Hunting Grounds", "a Hunting Grounds"]
    types = [Types.ACTION]
    cost = [6, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class IRONMONGER(CardInfo):
    names = ["Ironmonger", "Ironmongers", "an Ironmonger"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class JUNK_DEALER(CardInfo):
    names = ["Junk Dealer", "Junk Dealers", "a Junk Dealer"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class MADMAN(CardInfo):
    names = ["Madman", "Madmen", "a Madman"]
    types = [Types.ACTION]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class MARKET_SQUARE(CardInfo):
    names = ["Market Square", "Market Squares", "a Market Square"]
    types = [Types.ACTION, Types.REACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class MARAUDER(CardInfo):
    names = ["Marauder", "Marauders", "a Marauder"]
    types = [Types.ACTION, Types.ATTACK, Types.LOOTER]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class MERCENARY(CardInfo):
    names = ["Mercenary", "Mercenaries", "a Mercenary"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class MYSTIC(CardInfo):
    names = ["Mystic", "Mystics", "a Mystic"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class NECROPOLIS(CardInfo):
    names = ["Necropolis", "Necropolis", "a Necropolis"]
    types = [Types.ACTION, Types.SHELTER]
    cost = [1, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class OVERGROWN_ESTATE(CardInfo):
    names = ["Overgrown Estate", "Overgrown Estates", "an Overgrown Estate"]
    types = [Types.VICTORY, Types.SHELTER]
    cost = [1, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class PILLAGE(CardInfo):
    names = ["Pillage", "Pillages", "a Pillage"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class POOR_HOUSE(CardInfo):
    names = ["Poor House", "Poor Houses", "a Poor House"]
    types = [Types.ACTION]
    cost = [1, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class PROCESSION(CardInfo):
    names = ["Procession", "Processions", "a Procession"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class RATS(CardInfo):
    names = ["Rats", "Rats", "a Rats"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class REBUILD(CardInfo):
    names = ["Rebuild", "Rebuilds", "a Rebuild"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ROGUE(CardInfo):
    names = ["Rogue", "Rogues", "a Rogue"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class RUINED_LIBRARY(CardInfo):
    names = ["Ruined Library", "Ruined Libraries", "a Ruined Library"]
    types = [Types.ACTION, Types.RUINS]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class RUINED_MARKET(CardInfo):
    names = ["Ruined Market", "Ruined Markets", "a Ruined Market"]
    types = [Types.ACTION, Types.RUINS]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class RUINED_VILLAGE(CardInfo):
    names = ["Ruined Village", "Ruined Villages", "a Ruined Village"]
    types = [Types.ACTION, Types.RUINS]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SAGE(CardInfo):
    names = ["Sage", "Sages", "a Sage"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SCAVENGER(CardInfo):
    names = ["Scavenger", "Scavengers", "a Scavenger"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SIR_BAILEY(CardInfo):
    names = ["Sir Bailey", "Sir Baileys", "Sir Bailey"]
    types = [Types.ACTION, Types.ATTACK, Types.KNIGHT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SIR_DESTRY(CardInfo):
    names = ["Sir Destry", "Sir Destries", "Sir Destry"]
    types = [Types.ACTION, Types.ATTACK, Types.KNIGHT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SIR_MARTIN(CardInfo):
    names = ["Sir Martin", "Sir Martins", "Sir Martin"]
    types = [Types.ACTION, Types.ATTACK, Types.KNIGHT]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SIR_MICHAEL(CardInfo):
    names = ["Sir Michael", "Sir Michaels", "Sir Michael"]
    types = [Types.ACTION, Types.ATTACK, Types.KNIGHT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SIR_VANDER(CardInfo):
    names = ["Sir Vander", "Sir Vanders", "Sir Vander"]
    types = [Types.ACTION, Types.ATTACK, Types.KNIGHT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SPOILS(CardInfo):
    names = ["Spoils", "Spoils", "a Spoils"]
    types = [Types.TREASURE]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class STOREROOM(CardInfo):
    names = ["Storeroom", "Storerooms", "a Storeroom"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SQUIRE(CardInfo):
    names = ["Squire", "Squires", "a Squire"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SURVIVORS(CardInfo):
    names = ["Survivors", "Survivors", "a Survivors"]
    types = [Types.ACTION, Types.RUINS]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class URCHIN(CardInfo):
    names = ["Urchin", "Urchins", "an Urchin"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class VAGRANT(CardInfo):
    names = ["Vagrant", "Vagrants", "a Vagrant"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WANDERING_MINSTREL(CardInfo):
    names = ["Wandering Minstrel", "Wandering Minstrels", "a Wandering Minstrel"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ADVISOR(CardInfo):
    names = ["Advisor", "Advisors", "an Advisor"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BAKER(CardInfo):
    names = ["Baker", "Bakers", "a Baker"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BUTCHER(CardInfo):
    names = ["Butcher", "Butchers", "a Butcher"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CANDLESTICK_MAKER(CardInfo):
    names = ["Candlestick Maker", "Candlestick Makers", "a Candlestick Maker"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DOCTOR(CardInfo):
    names = ["Doctor", "Doctors", "a Doctor"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class HERALD(CardInfo):
    names = ["Herald", "Heralds", "a Herald"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class JOURNEYMAN(CardInfo):
    names = ["Journeyman", "Journeymen", "a Journeyman"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class MASTERPIECE(CardInfo):
    names = ["Masterpiece", "Masterpieces", "a Masterpiece"]
    types = [Types.TREASURE]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class MERCHANT_GUILD(CardInfo):
    names = ["Merchant Guild", "Merchant Guilds", "a Merchant Guild"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class PLAZA(CardInfo):
    names = ["Plaza", "Plazas", "a Plaza"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TAXMAN(CardInfo):
    names = ["Taxman", "Taxmen", "a Taxman"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SOOTHSAYER(CardInfo):
    names = ["Soothsayer", "Soothsayers", "a Soothsayer"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class STONEMASON(CardInfo):
    names = ["Stonemason", "Stonemasons", "a Stonemason"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ALMS(CardInfo):
    names = ["Alms", "Alms", "an Alms"]
    types = [Types.EVENT]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class AMULET(CardInfo):
    names = ["Amulet", "Amulets", "an Amulet"]
    types = [Types.ACTION, Types.DURATION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ARTIFICER(CardInfo):
    names = ["Artificer", "Artificers", "an Artificer"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BALL(CardInfo):
    names = ["Ball", "Balls", "a Ball"]
    types = [Types.EVENT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BONFIRE(CardInfo):
    names = ["Bonfire", "Bonfires", "a Bonfire"]
    types = [Types.EVENT]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BORROW(CardInfo):
    names = ["Borrow", "Borrows", "a Borrow"]
    types = [Types.EVENT]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BRIDGE_TROLL(CardInfo):
    names = ["Bridge Troll", "Bridge Trolls", "a Bridge Troll"]
    types = [Types.ACTION, Types.DURATION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CARAVAN_GUARD(CardInfo):
    names = ["Caravan Guard", "Caravan Guards", "a Caravan Guard"]
    types = [Types.ACTION, Types.DURATION, Types.REACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CHAMPION(CardInfo):
    names = ["Champion", "Champions", "a Champion"]
    types = [Types.ACTION, Types.DURATION]
    cost = [6, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class COIN_OF_THE_REALM(CardInfo):
    names = ["Coin of the Realm", "Coins of the Realm", "a Coin of the Realm"]
    types = [Types.TREASURE, Types.RESERVE]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DISCIPLE(CardInfo):
    names = ["Disciple", "Disciples", "a Disciple"]
    types = [Types.ACTION, Types.TRAVELLER]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DISTANT_LANDS(CardInfo):
    names = ["Distant Lands", "Distant Lands", "a Distant Lands"]
    types = [Types.ACTION, Types.RESERVE, Types.VICTORY]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DUNGEON(CardInfo):
    names = ["Dungeon", "Dungeons", "a Dungeon"]
    types = [Types.ACTION, Types.DURATION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DUPLICATE(CardInfo):
    names = ["Duplicate", "Duplicates", "a Duplicate"]
    types = [Types.ACTION, Types.RESERVE]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class EXPEDITION(CardInfo):
    names = ["Expedition", "Expeditions", "an Expedition"]
    types = [Types.EVENT]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class FERRY(CardInfo):
    names = ["Ferry", "Ferries", "a Ferry"]
    types = [Types.EVENT]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class FUGITIVE(CardInfo):
    names = ["Fugitive", "Fugitives", "a Fugitive"]
    types = [Types.ACTION, Types.TRAVELLER]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class GEAR(CardInfo):
    names = ["Gear", "Gears", "a Gear"]
    types = [Types.ACTION, Types.DURATION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class GIANT(CardInfo):
    names = ["Giant", "Giants", "a Giant"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class GUIDE(CardInfo):
    names = ["Guide", "Guides", "a Guide"]
    types = [Types.ACTION, Types.RESERVE]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class HAUNTED_WOODS(CardInfo):
    names = ["Haunted Woods", "Haunted Woods", "a Haunted Woods"]
    types = [Types.ACTION, Types.DURATION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class HERO(CardInfo):
    names = ["Hero", "Heroes", "a Hero"]
    types = [Types.ACTION, Types.TRAVELLER]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class HIRELING(CardInfo):
    names = ["Hireling", "Hirelings", "a Hireling"]
    types = [Types.ACTION, Types.DURATION]
    cost = [6, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class INHERITANCE(CardInfo):
    names = ["Inheritance", "Inheritances", "an Inheritance"]
    types = [Types.EVENT]
    cost = [7, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class LOST_ARTS(CardInfo):
    names = ["Lost Arts", "Lost Arts", "a Lost Arts"]
    types = [Types.EVENT]
    cost = [6, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class LOST_CITY(CardInfo):
    names = ["Lost City", "Lost Cities", "a Lost City"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class MAGPIE(CardInfo):
    names = ["Magpie", "Magpies", "a Magpie"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class MESSENGER(CardInfo):
    names = ["Messenger", "Messengers", "a Messenger"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class MISER(CardInfo):
    names = ["Miser", "Misers", "a Miser"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class MISSION(CardInfo):
    names = ["Mission", "Missions", "a Mission"]
    types = [Types.EVENT]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class PATHFINDING(CardInfo):
    names = ["Pathfinding", "Pathfindings", "a Pathfinding"]
    types = [Types.EVENT]
    cost = [8, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class PAGE(CardInfo):
    names = ["Page", "Pages", "a Page"]
    types = [Types.ACTION, Types.TRAVELLER]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class PEASANT(CardInfo):
    names = ["Peasant", "Peasants", "a Peasant"]
    types = [Types.ACTION, Types.TRAVELLER]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class PILGRIMAGE(CardInfo):
    names = ["Pilgrimage", "Pilgrimages", "a Pilgrimage"]
    types = [Types.EVENT]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class PLAN(CardInfo):
    names = ["Plan", "Plans", "a Plan"]
    types = [Types.EVENT]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class PORT(CardInfo):
    names = ["Port", "Ports", "a Port"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class QUEST(CardInfo):
    names = ["Quest", "Quests", "a Quest"]
    types = [Types.EVENT]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class RANGER(CardInfo):
    names = ["Ranger", "Rangers", "a Ranger"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class RAID(CardInfo):
    names = ["Raid", "Raids", "a Raid"]
    types = [Types.EVENT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class RATCATCHER(CardInfo):
    names = ["Ratcatcher", "Ratcatchers", "a Ratcatcher"]
    types = [Types.ACTION, Types.RESERVE]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class RAZE(CardInfo):
    names = ["Raze", "Razes", "a Raze"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class RELIC(CardInfo):
    names = ["Relic", "Relics", "a Relic"]
    types = [Types.TREASURE, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ROYAL_CARRIAGE(CardInfo):
    names = ["Royal Carriage", "Royal Carriages", "a Royal Carriage"]
    types = [Types.ACTION, Types.RESERVE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SAVE(CardInfo):
    names = ["Save", "Saves", "a Save"]
    types = [Types.EVENT]
    cost = [1, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SCOUTING_PARTY(CardInfo):
    names = ["Scouting Party", "Scouting Parties", "a Scouting Party"]
    types = [Types.EVENT]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SEAWAY(CardInfo):
    names = ["Seaway", "Seaways", "a Seaway"]
    types = [Types.EVENT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SOLDIER(CardInfo):
    names = ["Soldier", "Soldiers", "a Soldier"]
    types = [Types.ACTION, Types.ATTACK, Types.TRAVELLER]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class STORYTELLER(CardInfo):
    names = ["Storyteller", "Storytellers", "a Storyteller"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SWAMP_HAG(CardInfo):
    names = ["Swamp Hag", "Swamp Hags", "a Swamp Hag"]
    types = [Types.ACTION, Types.DURATION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TEACHER(CardInfo):
    names = ["Teacher", "Teachers", "a Teacher"]
    types = [Types.ACTION, Types.RESERVE]
    cost = [6, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TRAVELLING_FAIR(CardInfo):
    names = ["Travelling Fair", "Travelling Fairs", "a Travelling Fair"]
    types = [Types.EVENT]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TRADE(CardInfo):
    names = ["Trade", "Trades", "a Trade"]
    types = [Types.EVENT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TRAINING(CardInfo):
    names = ["Training", "Trainings", "a Training"]
    types = [Types.EVENT]
    cost = [6, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TRANSMOGRIFY(CardInfo):
    names = ["Transmogrify", "Transmogrifies", "a Transmogrify"]
    types = [Types.ACTION, Types.RESERVE]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TREASURE_TROVE(CardInfo):
    names = ["Treasure Trove", "Treasure Troves", "a Treasure Trove"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TREASURE_HUNTER(CardInfo):
    names = ["Treasure Hunter", "Treasure Hunters", "a Treasure Hunter"]
    types = [Types.ACTION, Types.TRAVELLER]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WARRIOR(CardInfo):
    names = ["Warrior", "Warriors", "a Warrior"]
    types = [Types.ACTION, Types.ATTACK, Types.TRAVELLER]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WINE_MERCHANT(CardInfo):
    names = ["Wine Merchant", "Wine Merchants", "a Wine Merchant"]
    types = [Types.ACTION, Types.RESERVE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ENCAMPMENT(CardInfo):
    names = ["Encampment", "Encampments", "an Encampment"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class PLUNDER(CardInfo):
    names = ["Plunder", "Plunders", "a Plunder"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class PATRICIAN(CardInfo):
    names = ["Patrician", "Patricians", "a Patrician"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class EMPORIUM(CardInfo):
    names = ["Emporium", "Emporia", "an Emporium"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SETTLERS(CardInfo):
    names = ["Settlers", "Settlers", "a Settlers"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BUSTLING_VILLAGE(CardInfo):
    names = ["Bustling Village", "Bustling Villages", "a Bustling Village"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CATAPULT(CardInfo):
    names = ["Catapult", "Catapults", "a Catapult"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ROCKS(CardInfo):
    names = ["Rocks", "Rocks", "a Rocks"]
    types = [Types.TREASURE]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class GLADIATOR(CardInfo):
    names = ["Gladiator", "Gladiators", "a Gladiator"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class FORTUNE(CardInfo):
    names = ["Fortune", "Fortunes", "a Fortune"]
    types = [Types.TREASURE]
    cost = [8, 0, 8]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CASTLES(CardInfo):
    names = ["Castles", "Castles", "a Castles"]
    types = [Types.VICTORY, Types.CASTLE]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class HUMBLE_CASTLE(CardInfo):
    names = ["Humble Castle", "Humble Castles", "a Humble Castle"]
    types = [Types.TREASURE, Types.VICTORY, Types.CASTLE]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CRUMBLING_CASTLE(CardInfo):
    names = ["Crumbling Castle", "Crumbling Castles", "a Crumbling Castle"]
    types = [Types.VICTORY, Types.CASTLE]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SMALL_CASTLE(CardInfo):
    names = ["Small Castle", "Small Castles", "a Small Castle"]
    types = [Types.ACTION, Types.VICTORY, Types.CASTLE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class HAUNTED_CASTLE(CardInfo):
    names = ["Haunted Castle", "Haunted Castles", "a Haunted Castle"]
    types = [Types.VICTORY, Types.CASTLE]
    cost = [6, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class OPULENT_CASTLE(CardInfo):
    names = ["Opulent Castle", "Opulent Castles", "an Opulent Castle"]
    types = [Types.ACTION, Types.VICTORY, Types.CASTLE]
    cost = [7, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SPRAWLING_CASTLE(CardInfo):
    names = ["Sprawling Castle", "Sprawling Castles", "a Sprawling Castle"]
    types = [Types.VICTORY, Types.CASTLE]
    cost = [8, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class GRAND_CASTLE(CardInfo):
    names = ["Grand Castle", "Grand Castles", "a Grand Castle"]
    types = [Types.VICTORY, Types.CASTLE]
    cost = [9, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class KINGS_CASTLE(CardInfo):
    names = ["King's Castle", "King's Castles", "a King's Castle"]
    types = [Types.VICTORY, Types.CASTLE]
    cost = [10, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ADVANCE(CardInfo):
    names = ["Advance", "Advances", "an Advance"]
    types = [Types.EVENT]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ANNEX(CardInfo):
    names = ["Annex", "Annexes", "an Annex"]
    types = [Types.EVENT]
    cost = [0, 0, 8]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ARCHIVE(CardInfo):
    names = ["Archive", "Archives", "an Archive"]
    types = [Types.ACTION, Types.DURATION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class AQUEDUCT(CardInfo):
    names = ["Aqueduct", "Aqueducts", "an Aqueduct"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ARENA(CardInfo):
    names = ["Arena", "Arenas", "an Arena"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BANDIT_FORT(CardInfo):
    names = ["Bandit Fort", "Bandit Forts", "a Bandit Fort"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BANQUET(CardInfo):
    names = ["Banquet", "Banquets", "a Banquet"]
    types = [Types.EVENT]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BASILICA(CardInfo):
    names = ["Basilica", "Basilicas", "a Basilica"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BATHS(CardInfo):
    names = ["Baths", "Baths", "a Baths"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BATTLEFIELD(CardInfo):
    names = ["Battlefield", "Battlefields", "a Battlefield"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CAPITAL(CardInfo):
    names = ["Capital", "Capitals", "a Capital"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CHARM(CardInfo):
    names = ["Charm", "Charms", "a Charm"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CHARIOT_RACE(CardInfo):
    names = ["Chariot Race", "Chariot Races", "a Chariot Race"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CITY_QUARTER(CardInfo):
    names = ["City Quarter", "City Quarters", "a City Quarter"]
    types = [Types.ACTION]
    cost = [0, 0, 8]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class COLONNADE(CardInfo):
    names = ["Colonnade", "Colonnades", "a Colonnade"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CONQUEST(CardInfo):
    names = ["Conquest", "Conquests", "a Conquest"]
    types = [Types.EVENT]
    cost = [6, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CROWN(CardInfo):
    names = ["Crown", "Crowns", "a Crown"]
    types = [Types.ACTION, Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DELVE(CardInfo):
    names = ["Delve", "Delves", "a Delve"]
    types = [Types.EVENT]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DEFILED_SHRINE(CardInfo):
    names = ["Defiled Shrine", "Defiled Shrines", "a Defiled Shrine"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DOMINATE(CardInfo):
    names = ["Dominate", "Dominates", "a Dominate"]
    types = [Types.EVENT]
    cost = [14, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DONATE(CardInfo):
    names = ["Donate", "Donates", "a Donate"]
    types = [Types.EVENT]
    cost = [0, 0, 8]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ENCHANTRESS(CardInfo):
    names = ["Enchantress", "Enchantresses", "an Enchantress"]
    types = [Types.ACTION, Types.DURATION, Types.ATTACK]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ENGINEER(CardInfo):
    names = ["Engineer", "Engineers", "an Engineer"]
    types = [Types.ACTION]
    cost = [0, 0, 4]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class FARMERS_MARKET(CardInfo):
    names = ["Farmers' Market", "Farmers' Markets", "a Farmers' Market"]
    types = [Types.ACTION, Types.GATHERING]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class FORUM(CardInfo):
    names = ["Forum", "Forums", "a Forum"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class FOUNTAIN(CardInfo):
    names = ["Fountain", "Fountains", "a Fountain"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class GROUNDSKEEPER(CardInfo):
    names = ["Groundskeeper", "Groundskeepers", "a Groundskeeper"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class KEEP(CardInfo):
    names = ["Keep", "Keeps", "a Keep"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class LABYRINTH(CardInfo):
    names = ["Labyrinth", "Labyrinths", "a Labyrinth"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class LEGIONARY(CardInfo):
    names = ["Legionary", "Legionaries", "a Legionary"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class MOUNTAIN_PASS(CardInfo):
    names = ["Mountain Pass", "Mountain Passes", "a Mountain Pass"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class MUSEUM(CardInfo):
    names = ["Museum", "Museums", "a Museum"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class OBELISK(CardInfo):
    names = ["Obelisk", "Obelisks", "an Obelisk"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ORCHARD(CardInfo):
    names = ["Orchard", "Orchards", "an Orchard"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class OVERLORD(CardInfo):
    names = ["Overlord", "Overlords", "an Overlord"]
    types = [Types.ACTION, Types.COMMAND]
    cost = [0, 0, 8]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class PALACE(CardInfo):
    names = ["Palace", "Palaces", "a Palace"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class RITUAL(CardInfo):
    names = ["Ritual", "Rituals", "a Ritual"]
    types = [Types.EVENT]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ROYAL_BLACKSMITH(CardInfo):
    names = ["Royal Blacksmith", "Royal Blacksmiths", "a Royal Blacksmith"]
    types = [Types.ACTION]
    cost = [0, 0, 8]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SACRIFICE(CardInfo):
    names = ["Sacrifice", "Sacrifices", "a Sacrifice"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SALT_THE_EARTH(CardInfo):
    names = ["Salt the Earth", "Salt the Earths", "a Salt the Earth"]
    types = [Types.EVENT]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TAX(CardInfo):
    names = ["Tax", "Taxes", "a Tax"]
    types = [Types.EVENT]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TEMPLE(CardInfo):
    names = ["Temple", "Temples", "a Temple"]
    types = [Types.ACTION, Types.GATHERING]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TOMB(CardInfo):
    names = ["Tomb", "Tombs", "a Tomb"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TOWER(CardInfo):
    names = ["Tower", "Towers", "a Tower"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TRIUMPH(CardInfo):
    names = ["Triumph", "Triumphs", "a Triumph"]
    types = [Types.EVENT]
    cost = [0, 0, 5]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TRIUMPHAL_ARCH(CardInfo):
    names = ["Triumphal Arch", "Triumphal Arches", "a Triumphal Arch"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class VILLA(CardInfo):
    names = ["Villa", "Villas", "a Villa"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WALL(CardInfo):
    names = ["Wall", "Walls", "a Wall"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WOLF_DEN(CardInfo):
    names = ["Wolf Den", "Wolf Dens", "a Wolf Den"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WEDDING(CardInfo):
    names = ["Wedding", "Weddings", "a Wedding"]
    types = [Types.EVENT]
    cost = [4, 0, 3]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WILD_HUNT(CardInfo):
    names = ["Wild Hunt", "Wild Hunts", "a Wild Hunt"]
    types = [Types.ACTION, Types.GATHERING]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WINDFALL(CardInfo):
    names = ["Windfall", "Windfalls", "a Windfall"]
    types = [Types.EVENT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class THE_EARTHS_GIFT(CardInfo):
    names = ["The Earth's Gift", "The Earth's Gifts", "The Earth's Gift"]
    types = [Types.BOON]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class THE_FIELDS_GIFT(CardInfo):
    names = ["The Field's Gift", "The Field's Gifts", "The Field's Gift"]
    types = [Types.BOON]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class THE_FLAMES_GIFT(CardInfo):
    names = ["The Flame's Gift", "The Flame's Gifts", "The Flame's Gift"]
    types = [Types.BOON]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class THE_FORESTS_GIFT(CardInfo):
    names = ["The Forest's Gift", "The Forest's Gifts", "The Forest's Gift"]
    types = [Types.BOON]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class THE_MOONS_GIFT(CardInfo):
    names = ["The Moon's Gift", "The Moon's Gifts", "The Moon's Gift"]
    types = [Types.BOON]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class THE_MOUNTAINS_GIFT(CardInfo):
    names = ["The Mountain's Gift", "The Mountain's Gifts", "The Mountain's Gift"]
    types = [Types.BOON]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class THE_RIVERS_GIFT(CardInfo):
    names = ["The River's Gift", "The River's Gifts", "The River's Gift"]
    types = [Types.BOON]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class THE_SEAS_GIFT(CardInfo):
    names = ["The Sea's Gift", "The Sea's Gifts", "The Sea's Gift"]
    types = [Types.BOON]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class THE_SKYS_GIFT(CardInfo):
    names = ["The Sky's Gift", "The Sky's Gifts", "The Sky's Gift"]
    types = [Types.BOON]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class THE_SUNS_GIFT(CardInfo):
    names = ["The Sun's Gift", "The Sun's Gifts", "The Sun's Gift"]
    types = [Types.BOON]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class THE_SWAMPS_GIFT(CardInfo):
    names = ["The Swamp's Gift", "The Swamp's Gifts", "The Swamp's Gift"]
    types = [Types.BOON]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class THE_WINDS_GIFT(CardInfo):
    names = ["The Wind's Gift", "The Wind's Gifts", "The Wind's Gift"]
    types = [Types.BOON]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BAD_OMENS(CardInfo):
    names = ["Bad Omens", "Bad Omens", "Bad Omens"]
    types = [Types.HEX]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DELUSION(CardInfo):
    names = ["Delusion", "Delusions", "Delusion"]
    types = [Types.HEX]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ENVY(CardInfo):
    names = ["Envy", "Envies", "Envy"]
    types = [Types.HEX]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class FAMINE(CardInfo):
    names = ["Famine", "Famines", "Famine"]
    types = [Types.HEX]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class FEAR(CardInfo):
    names = ["Fear", "Fears", "Fear"]
    types = [Types.HEX]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class GREED(CardInfo):
    names = ["Greed", "Greeds", "Greed"]
    types = [Types.HEX]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class HAUNTING(CardInfo):
    names = ["Haunting", "Hauntings", "Haunting"]
    types = [Types.HEX]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class LOCUSTS(CardInfo):
    names = ["Locusts", "Locusts", "Locusts"]
    types = [Types.HEX]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class MISERY(CardInfo):
    names = ["Misery", "Miseries", "Misery"]
    types = [Types.HEX]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class PLAGUE(CardInfo):
    names = ["Plague", "Plagues", "Plague"]
    types = [Types.HEX]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class POVERTY(CardInfo):
    names = ["Poverty", "Poverties", "Poverty"]
    types = [Types.HEX]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WAR(CardInfo):
    names = ["War", "Wars", "War"]
    types = [Types.HEX]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class MISERABLE(CardInfo):
    names = ["Miserable", "Miserables", "Miserable"]
    types = [Types.STATE]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TWICE_MISERABLE(CardInfo):
    names = ["Twice Miserable", "Twice Miserables", "Twice Miserable"]
    types = [Types.STATE]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ENVIOUS(CardInfo):
    names = ["Envious", "Envious", "Envious"]
    types = [Types.STATE]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DELUDED(CardInfo):
    names = ["Deluded", "Deludeds", "Deluded"]
    types = [Types.STATE]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class LOST_IN_THE_WOODS(CardInfo):
    names = ["Lost In The Woods", "Lost In The Woods", "Lost In The Woods"]
    types = [Types.STATE]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BARD(CardInfo):
    names = ["Bard", "Bards", "a Bard"]
    types = [Types.ACTION, Types.FATE]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BLESSED_VILLAGE(CardInfo):
    names = ["Blessed Village", "Blessed Villages", "a Blessed Village"]
    types = [Types.ACTION, Types.FATE]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CHANGELING(CardInfo):
    names = ["Changeling", "Changelings", "a Changeling"]
    types = [Types.NIGHT]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CEMETERY(CardInfo):
    names = ["Cemetery", "Cemeteries", "a Cemetery"]
    types = [Types.VICTORY]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class COBBLER(CardInfo):
    names = ["Cobbler", "Cobblers", "a Cobbler"]
    types = [Types.NIGHT, Types.DURATION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CONCLAVE(CardInfo):
    names = ["Conclave", "Conclaves", "a Conclave"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CRYPT(CardInfo):
    names = ["Crypt", "Crypts", "a Crypt"]
    types = [Types.NIGHT, Types.DURATION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CURSED_VILLAGE(CardInfo):
    names = ["Cursed Village", "Cursed Villages", "a Cursed Village"]
    types = [Types.ACTION, Types.DOOM]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DEN_OF_SIN(CardInfo):
    names = ["Den of Sin", "Dens of Sin", "a Den of Sin"]
    types = [Types.NIGHT, Types.DURATION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DEVILS_WORKSHOP(CardInfo):
    names = ["Devil's Workshop", "Devil's Workshops", "a Devil's Workshop"]
    types = [Types.NIGHT]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DRUID(CardInfo):
    names = ["Druid", "Druids", "a Druid"]
    types = [Types.ACTION, Types.FATE]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class EXORCIST(CardInfo):
    names = ["Exorcist", "Exorcists", "an Exorcist"]
    types = [Types.NIGHT]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class FAITHFUL_HOUND(CardInfo):
    names = ["Faithful Hound", "Faithful Hounds", "a Faithful Hound"]
    types = [Types.ACTION, Types.REACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class FOOL(CardInfo):
    names = ["Fool", "Fools", "a Fool"]
    types = [Types.ACTION, Types.FATE]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class GHOST_TOWN(CardInfo):
    names = ["Ghost Town", "Ghost Towns", "a Ghost Town"]
    types = [Types.NIGHT, Types.DURATION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class GUARDIAN(CardInfo):
    names = ["Guardian", "Guardians", "a Guardian"]
    types = [Types.NIGHT, Types.DURATION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class IDOL(CardInfo):
    names = ["Idol", "Idols", "an Idol"]
    types = [Types.TREASURE, Types.ATTACK, Types.FATE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class LEPRECHAUN(CardInfo):
    names = ["Leprechaun", "Leprechauns", "a Leprechaun"]
    types = [Types.ACTION, Types.DOOM]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class MONASTERY(CardInfo):
    names = ["Monastery", "Monasteries", "a Monastery"]
    types = [Types.NIGHT]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class NECROMANCER(CardInfo):
    names = ["Necromancer", "Necromancers", "a Necromancer"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class NIGHT_WATCHMAN(CardInfo):
    names = ["Night Watchman", "Night Watchmen", "a Night Watchman"]
    types = [Types.NIGHT]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class PIXIE(CardInfo):
    names = ["Pixie", "Pixies", "a Pixie"]
    types = [Types.ACTION, Types.FATE]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class POOKA(CardInfo):
    names = ["Pooka", "Pookas", "a Pooka"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class RAIDER(CardInfo):
    names = ["Raider", "Raiders", "a Raider"]
    types = [Types.NIGHT, Types.DURATION, Types.ATTACK]
    cost = [6, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SACRED_GROVE(CardInfo):
    names = ["Sacred Grove", "Sacred Groves", "a Sacred Grove"]
    types = [Types.ACTION, Types.FATE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SECRET_CAVE(CardInfo):
    names = ["Secret Cave", "Secret Caves", "a Secret Cave"]
    types = [Types.ACTION, Types.DURATION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SHEPHERD(CardInfo):
    names = ["Shepherd", "Shepherds", "a Shepherd"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SKULK(CardInfo):
    names = ["Skulk", "Skulks", "a Skulk"]
    types = [Types.ACTION, Types.ATTACK, Types.DOOM]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TORMENTOR(CardInfo):
    names = ["Tormentor", "Tormentors", "a Tormentor"]
    types = [Types.ACTION, Types.ATTACK, Types.DOOM]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TRAGIC_HERO(CardInfo):
    names = ["Tragic Hero", "Tragic Heroes", "a Tragic Hero"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TRACKER(CardInfo):
    names = ["Tracker", "Trackers", "a Tracker"]
    types = [Types.ACTION, Types.FATE]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class VAMPIRE(CardInfo):
    names = ["Vampire", "Vampires", "a Vampire"]
    types = [Types.NIGHT, Types.ATTACK, Types.DOOM]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WEREWOLF(CardInfo):
    names = ["Werewolf", "Werewolves", "a Werewolf"]
    types = [Types.ACTION, Types.NIGHT, Types.ATTACK, Types.DOOM]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CURSED_GOLD(CardInfo):
    names = ["Cursed Gold", "Cursed Golds", "a Cursed Gold"]
    types = [Types.TREASURE, Types.HEIRLOOM]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class GOAT(CardInfo):
    names = ["Goat", "Goats", "a Goat"]
    types = [Types.TREASURE, Types.HEIRLOOM]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class HAUNTED_MIRROR(CardInfo):
    names = ["Haunted Mirror", "Haunted Mirrors", "a Haunted Mirror"]
    types = [Types.TREASURE, Types.HEIRLOOM]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class LUCKY_COIN(CardInfo):
    names = ["Lucky Coin", "Lucky Coins", "a Lucky Coin"]
    types = [Types.TREASURE, Types.HEIRLOOM]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class MAGIC_LAMP(CardInfo):
    names = ["Magic Lamp", "Magic Lamps", "a Magic Lamp"]
    types = [Types.TREASURE, Types.HEIRLOOM]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class PASTURE(CardInfo):
    names = ["Pasture", "Pastures", "a Pasture"]
    types = [Types.TREASURE, Types.VICTORY, Types.HEIRLOOM]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class POUCH(CardInfo):
    names = ["Pouch", "Pouches", "a Pouch"]
    types = [Types.TREASURE, Types.HEIRLOOM]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BAT(CardInfo):
    names = ["Bat", "Bats", "a Bat"]
    types = [Types.NIGHT]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class GHOST(CardInfo):
    names = ["Ghost", "Ghosts", "a Ghost"]
    types = [Types.NIGHT, Types.DURATION, Types.SPIRIT]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class IMP(CardInfo):
    names = ["Imp", "Imps", "an Imp"]
    types = [Types.ACTION, Types.SPIRIT]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WILL_O_WISP(CardInfo):
    names = ["Will-o'-Wisp", "Will-o'-Wisps", "a Will-o'-Wisp"]
    types = [Types.ACTION, Types.SPIRIT]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WISH(CardInfo):
    names = ["Wish", "Wishes", "a Wish"]
    types = [Types.ACTION]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ZOMBIE_APPRENTICE(CardInfo):
    names = ["Zombie Apprentice", "Zombie Apprentices", "a Zombie Apprentice"]
    types = [Types.ACTION, Types.ZOMBIE]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ZOMBIE_MASON(CardInfo):
    names = ["Zombie Mason", "Zombie Masons", "a Zombie Mason"]
    types = [Types.ACTION, Types.ZOMBIE]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ZOMBIE_SPY(CardInfo):
    names = ["Zombie Spy", "Zombie Spies", "a Zombie Spy"]
    types = [Types.ACTION, Types.ZOMBIE]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ACTING_TROUPE(CardInfo):
    names = ["Acting Troupe", "Acting Troupes", "an Acting Troupe"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BORDER_GUARD(CardInfo):
    names = ["Border Guard", "Border Guards", "a Border Guard"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CARGO_SHIP(CardInfo):
    names = ["Cargo Ship", "Cargo Ships", "a Cargo Ship"]
    types = [Types.ACTION, Types.DURATION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DUCAT(CardInfo):
    names = ["Ducat", "Ducats", "a Ducat"]
    types = [Types.TREASURE]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class EXPERIMENT(CardInfo):
    names = ["Experiment", "Experiments", "an Experiment"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class FLAG_BEARER(CardInfo):
    names = ["Flag Bearer", "Flag Bearers", "a Flag Bearer"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class HIDEOUT(CardInfo):
    names = ["Hideout", "Hideouts", "a Hideout"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class INVENTOR(CardInfo):
    names = ["Inventor", "Inventors", "an Inventor"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class IMPROVE(CardInfo):
    names = ["Improve", "Improves", "an Improve"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class LACKEYS(CardInfo):
    names = ["Lackeys", "Lackeys", "a Lackeys"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class MOUNTAIN_VILLAGE(CardInfo):
    names = ["Mountain Village", "Mountain Villages", "a Mountain Village"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class PATRON(CardInfo):
    names = ["Patron", "Patrons", "a Patron"]
    types = [Types.ACTION, Types.REACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class PRIEST(CardInfo):
    names = ["Priest", "Priests", "a Priest"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class RESEARCH(CardInfo):
    names = ["Research", "Researches", "a Research"]
    types = [Types.ACTION, Types.DURATION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SILK_MERCHANT(CardInfo):
    names = ["Silk Merchant", "Silk Merchants", "a Silk Merchant"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class OLD_WITCH(CardInfo):
    names = ["Old Witch", "Old Witches", "an Old Witch"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class RECRUITER(CardInfo):
    names = ["Recruiter", "Recruiters", "a Recruiter"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SCEPTER(CardInfo):
    names = ["Scepter", "Scepters", "a Scepter"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SCHOLAR(CardInfo):
    names = ["Scholar", "Scholars", "a Scholar"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SCULPTOR(CardInfo):
    names = ["Sculptor", "Sculptors", "a Sculptor"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SEER(CardInfo):
    names = ["Seer", "Seers", "a Seer"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SPICES(CardInfo):
    names = ["Spices", "Spices", "a Spices"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SWASHBUCKLER(CardInfo):
    names = ["Swashbuckler", "Swashbucklers", "a Swashbuckler"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TREASURER(CardInfo):
    names = ["Treasurer", "Treasurers", "a Treasurer"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class VILLAIN(CardInfo):
    names = ["Villain", "Villains", "a Villain"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class FLAG(CardInfo):
    names = ["Flag", "Flags", "the Flag"]
    types = [Types.ARTIFACT]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class HORN(CardInfo):
    names = ["Horn", "Horns", "the Horn"]
    types = [Types.ARTIFACT]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class KEY(CardInfo):
    names = ["Key", "Keys", "the Key"]
    types = [Types.ARTIFACT]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class LANTERN(CardInfo):
    names = ["Lantern", "Lanterns", "the Lantern"]
    types = [Types.ARTIFACT]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TREASURE_CHEST(CardInfo):
    names = ["Treasure Chest", "Treasure Chests", "the Treasure Chest"]
    types = [Types.ARTIFACT]
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ACADEMY(CardInfo):
    names = ["Academy", "Academy", "Academy"]
    types = [Types.PROJECT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BARRACKS(CardInfo):
    names = ["Barracks", "Barracks", "Barracks"]
    types = [Types.PROJECT]
    cost = [6, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CANAL(CardInfo):
    names = ["Canal", "Canal", "Canal"]
    types = [Types.PROJECT]
    cost = [7, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CAPITALISM(CardInfo):
    names = ["Capitalism", "Capitalism", "Capitalism"]
    types = [Types.PROJECT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CATHEDRAL(CardInfo):
    names = ["Cathedral", "Cathedral", "Cathedral"]
    types = [Types.PROJECT]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CITADEL(CardInfo):
    names = ["Citadel", "Citadel", "Citadel"]
    types = [Types.PROJECT]
    cost = [8, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CITY_GATE(CardInfo):
    names = ["City Gate", "City Gate", "City Gate"]
    types = [Types.PROJECT]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CROP_ROTATION(CardInfo):
    names = ["Crop Rotation", "Crop Rotation", "Crop Rotation"]
    types = [Types.PROJECT]
    cost = [6, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class EXPLORATION(CardInfo):
    names = ["Exploration", "Exploration", "Exploration"]
    types = [Types.PROJECT]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class FAIR(CardInfo):
    names = ["Fair", "Fair", "Fair"]
    types = [Types.PROJECT]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class FLEET(CardInfo):
    names = ["Fleet", "Fleet", "Fleet"]
    types = [Types.PROJECT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class GUILDHALL(CardInfo):
    names = ["Guildhall", "Guildhall", "Guildhall"]
    types = [Types.PROJECT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class INNOVATION(CardInfo):
    names = ["Innovation", "Innovation", "Innovation"]
    types = [Types.PROJECT]
    cost = [6, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class PAGEANT(CardInfo):
    names = ["Pageant", "Pageant", "Pageant"]
    types = [Types.PROJECT]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class PIAZZA(CardInfo):
    names = ["Piazza", "Piazza", "Piazza"]
    types = [Types.PROJECT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ROAD_NETWORK(CardInfo):
    names = ["Road Network", "Road Network", "Road Network"]
    types = [Types.PROJECT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SEWERS(CardInfo):
    names = ["Sewers", "Sewers", "Sewers"]
    types = [Types.PROJECT]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SILOS(CardInfo):
    names = ["Silos", "Silos", "Silos"]
    types = [Types.PROJECT]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SINISTER_PLOT(CardInfo):
    names = ["Sinister Plot", "Sinister Plot", "Sinister Plot"]
    types = [Types.PROJECT]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class STAR_CHART(CardInfo):
    names = ["Star Chart", "Star Chart", "Star Chart"]
    types = [Types.PROJECT]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SAUNA(CardInfo):
    names = ["Sauna", "Saunas", "a Sauna"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class AVANTO(CardInfo):
    names = ["Avanto", "Avantos", "an Avanto"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BLACK_MARKET(CardInfo):
    names = ["Black Market", "Black Markets", "a Black Market"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ENVOY(CardInfo):
    names = ["Envoy", "Envoys", "an Envoy"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class GOVERNOR(CardInfo):
    names = ["Governor", "Governors", "a Governor"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class PRINCE(CardInfo):
    names = ["Prince", "Princes", "a Prince"]
    types = [Types.ACTION]
    cost = [8, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class STASH(CardInfo):
    names = ["Stash", "Stashes", "a Stash"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SUMMON(CardInfo):
    names = ["Summon", "Summons", "a Summon"]
    types = [Types.EVENT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WALLED_VILLAGE(CardInfo):
    names = ["Walled Village", "Walled Villages", "a Walled Village"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BLACK_MARKET_DECK(CardInfo):
    names = ["Black Market Deck", "Black Market Decks", "a Black Market Deck"]
    types = []
    cost = [0, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DISMANTLE(CardInfo):
    names = ["Dismantle", "Dismantles", "a Dismantle"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CAPTAIN(CardInfo):
    names = ["Captain", "Captains", "a Captain"]
    types = [Types.ACTION, Types.DURATION, Types.COMMAND]
    cost = [6, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CHURCH(CardInfo):
    names = ["Church", "Churches", "a Church"]
    types = [Types.ACTION, Types.DURATION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, realPlay):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BLACK_CAT(CardInfo):
    names = ["Black Cat", "Black Cats", "a Black Cat"]
    types = [Types.ACTION, Types.ATTACK, Types.REACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SLEIGH(CardInfo):
    names = ["Sleigh", "Sleighs", "a Sleigh"]
    types = [Types.ACTION, Types.REACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SUPPLIES(CardInfo):
    names = ["Supplies", "Supplies", "a Supplies"]
    types = [Types.TREASURE]
    cost = [2, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CAMEL_TRAIN(CardInfo):
    names = ["Camel Train", "Camel Trains", "a Camel Train"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class GOATHERD(CardInfo):
    names = ["Goatherd", "Goatherds", "a Goatherd"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SCRAP(CardInfo):
    names = ["Scrap", "Scraps", "a Scrap"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SHEEPDOG(CardInfo):
    names = ["Sheepdog", "Sheepdogs", "a Sheepdog"]
    types = [Types.ACTION, Types.REACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SNOWY_VILLAGE(CardInfo):
    names = ["Snowy Village", "Snowy Villages", "a Snowy Village"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class STOCKPILE(CardInfo):
    names = ["Stockpile", "Stockpiles", "a Stockpile"]
    types = [Types.TREASURE]
    cost = [3, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BOUNTY_HUNTER(CardInfo):
    names = ["Bounty Hunter", "Bounty Hunters", "a Bounty Hunter"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CARDINAL(CardInfo):
    names = ["Cardinal", "Cardinals", "a Cardinal"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [4, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class CAVALRY(CardInfo):
    names = ["Cavalry", "Cavalries", "a Cavalry"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class GROOM(CardInfo):
    names = ["Groom", "Grooms", "a Groom"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class HOSTELRY(CardInfo):
    names = ["Hostelry", "Hostelries", "a Hostelry"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class VILLAGE_GREEN(CardInfo):
    names = ["Village Green", "Village Greens", "a Village Green"]
    types = [Types.ACTION, Types.DURATION, Types.REACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BARGE(CardInfo):
    names = ["Barge", "Barges", "a Barge"]
    types = [Types.ACTION, Types.DURATION]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class COVEN(CardInfo):
    names = ["Coven", "Covens", "a Coven"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DISPLACE(CardInfo):
    names = ["Displace", "Displaces", "a Displace"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class FALCONER(CardInfo):
    names = ["Falconer", "Falconers", "a Falconer"]
    types = [Types.ACTION, Types.REACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class FISHERMAN(CardInfo):
    names = ["Fisherman", "Fishermen", "a Fisherman"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class GATEKEEPER(CardInfo):
    names = ["Gatekeeper", "Gatekeepers", "a Gatekeeper"]
    types = [Types.ACTION, Types.DURATION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class HUNTING_LODGE(CardInfo):
    names = ["Hunting Lodge", "Hunting Lodges", "a Hunting Lodge"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class KILN(CardInfo):
    names = ["Kiln", "Kilns", "a Kiln"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class LIVERY(CardInfo):
    names = ["Livery", "Liveries", "a Livery"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class MASTERMIND(CardInfo):
    names = ["Mastermind", "Masterminds", "a Mastermind"]
    types = [Types.ACTION, Types.DURATION]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class PADDOCK(CardInfo):
    names = ["Paddock", "Paddocks", "a Paddock"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SANCTUARY(CardInfo):
    names = ["Sanctuary", "Sanctuaries", "a Sanctuary"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DESTRIER(CardInfo):
    names = ["Destrier", "Destriers", "a Destrier"]
    types = [Types.ACTION]
    cost = [6, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WAYFARER(CardInfo):
    names = ["Wayfarer", "Wayfarers", "a Wayfarer"]
    types = [Types.ACTION]
    cost = [6, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ANIMAL_FAIR(CardInfo):
    names = ["Animal Fair", "Animal Fairs", "an Animal Fair"]
    types = [Types.ACTION]
    cost = [7, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class HORSE(CardInfo):
    names = ["Horse", "Horses", "a Horse"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WAY_OF_THE_BUTTERFLY(CardInfo):
    names = ["Way of the Butterfly", "Way of the Butterfly", "Way of the Butterfly"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WAY_OF_THE_CAMEL(CardInfo):
    names = ["Way of the Camel", "Way of the Camel", "Way of the Camel"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WAY_OF_THE_CHAMELEON(CardInfo):
    names = ["Way of the Chameleon", "Way of the Chameleon", "Way of the Chameleon"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WAY_OF_THE_FROG(CardInfo):
    names = ["Way of the Frog", "Way of the Frog", "Way of the Frog"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WAY_OF_THE_GOAT(CardInfo):
    names = ["Way of the Goat", "Way of the Goat", "Way of the Goat"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WAY_OF_THE_HORSE(CardInfo):
    names = ["Way of the Horse", "Way of the Horse", "Way of the Horse"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WAY_OF_THE_MOLE(CardInfo):
    names = ["Way of the Mole", "Way of the Mole", "Way of the Mole"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WAY_OF_THE_MONKEY(CardInfo):
    names = ["Way of the Monkey", "Way of the Monkey", "Way of the Monkey"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WAY_OF_THE_MOUSE(CardInfo):
    names = ["Way of the Mouse", "Way of the Mouse", "Way of the Mouse"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WAY_OF_THE_MULE(CardInfo):
    names = ["Way of the Mule", "Way of the Mule", "Way of the Mule"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WAY_OF_THE_OTTER(CardInfo):
    names = ["Way of the Otter", "Way of the Otter", "Way of the Otter"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WAY_OF_THE_OWL(CardInfo):
    names = ["Way of the Owl", "Way of the Owl", "Way of the Owl"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WAY_OF_THE_OX(CardInfo):
    names = ["Way of the Ox", "Way of the Ox", "Way of the Ox"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WAY_OF_THE_PIG(CardInfo):
    names = ["Way of the Pig", "Way of the Pig", "Way of the Pig"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WAY_OF_THE_RAT(CardInfo):
    names = ["Way of the Rat", "Way of the Rat", "Way of the Rat"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WAY_OF_THE_SEAL(CardInfo):
    names = ["Way of the Seal", "Way of the Seal", "Way of the Seal"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WAY_OF_THE_SHEEP(CardInfo):
    names = ["Way of the Sheep", "Way of the Sheep", "Way of the Sheep"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WAY_OF_THE_SQUIRREL(CardInfo):
    names = ["Way of the Squirrel", "Way of the Squirrel", "Way of the Squirrel"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WAY_OF_THE_TURTLE(CardInfo):
    names = ["Way of the Turtle", "Way of the Turtle", "Way of the Turtle"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class WAY_OF_THE_WORM(CardInfo):
    names = ["Way of the Worm", "Way of the Worm", "Way of the Worm"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DELAY(CardInfo):
    names = ["Delay", "Delay", "Delay"]
    types = [Types.EVENT]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DESPERATION(CardInfo):
    names = ["Desperation", "Desperation", "Desperation"]
    types = [Types.EVENT]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class GAMBLE(CardInfo):
    names = ["Gamble", "Gamble", "Gamble"]
    types = [Types.EVENT]
    cost = [2, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class PURSUE(CardInfo):
    names = ["Pursue", "Pursue", "Pursue"]
    types = [Types.EVENT]
    cost = [2, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class RIDE(CardInfo):
    names = ["Ride", "Ride", "Ride"]
    types = [Types.EVENT]
    cost = [2, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TOIL(CardInfo):
    names = ["Toil", "Toil", "Toil"]
    types = [Types.EVENT]
    cost = [2, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ENHANCE(CardInfo):
    names = ["Enhance", "Enhance", "Enhance"]
    types = [Types.EVENT]
    cost = [3, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class MARCH(CardInfo):
    names = ["March", "March", "March"]
    types = [Types.EVENT]
    cost = [3, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class TRANSPORT(CardInfo):
    names = ["Transport", "Transport", "Transport"]
    types = [Types.EVENT]
    cost = [3, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BANISH(CardInfo):
    names = ["Banish", "Banish", "Banish"]
    types = [Types.EVENT]
    cost = [4, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class BARGAIN(CardInfo):
    names = ["Bargain", "Bargain", "Bargain"]
    types = [Types.EVENT]
    cost = [4, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class INVEST(CardInfo):
    names = ["Invest", "Invest", "Invest"]
    types = [Types.EVENT]
    cost = [4, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class SEIZE_THE_DAY(CardInfo):
    names = ["Seize The Day", "Seize The Day", "Seize The Day"]
    types = [Types.EVENT]
    cost = [4, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class COMMERCE(CardInfo):
    names = ["Commerce", "Commerce", "Commerce"]
    types = [Types.EVENT]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class DEMAND(CardInfo):
    names = ["Demand", "Demand", "Demand"]
    types = [Types.EVENT]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class STAMPEDE(CardInfo):
    names = ["Stampede", "Stampede", "Stampede"]
    types = [Types.EVENT]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class REAP(CardInfo):
    names = ["Reap", "Reap", "Reap"]
    types = [Types.EVENT]
    cost = [7, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ENCLAVE(CardInfo):
    names = ["Enclave", "Enclave", "Enclave"]
    types = [Types.EVENT]
    cost = [8, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class ALLIANCE(CardInfo):
    names = ["Alliance", "Alliance", "Alliance"]
    types = [Types.EVENT]
    cost = [10, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


class POPULATE(CardInfo):
    names = ["Populate", "Populate", "Populate"]
    types = [Types.EVENT]
    cost = [10, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = [state.stack.pop()]
        return state


def getCardInfo(card):
    correspondences = {
        "Curse": CURSE,
        "Copper": COPPER,
        "Silver": SILVER,
        "Gold": GOLD,
        "Estate": ESTATE,
        "Duchy": DUCHY,
        "Province": PROVINCE,
        "Artisan": ARTISAN,
        "Bandit": BANDIT,
        "Bureaucrat": BUREAUCRAT,
        "Cellar": CELLAR,
        "Chapel": CHAPEL,
        "Council Room": COUNCIL_ROOM,
        "Festival": FESTIVAL,
        "Gardens": GARDENS,
        "Harbinger": HARBINGER,
        "Laboratory": LABORATORY,
        "Library": LIBRARY,
        "Market": MARKET,
        "Merchant": MERCHANT,
        "Militia": MILITIA,
        "Mine": MINE,
        "Moat": MOAT,
        "Moneylender": MONEYLENDER,
        "Poacher": POACHER,
        "Remodel": REMODEL,
        "Sentry": SENTRY,
        "Smithy": SMITHY,
        "Throne Room": THRONE_ROOM,
        "Vassal": VASSAL,
        "Village": VILLAGE,
        "Witch": WITCH,
        "Workshop": WORKSHOP,
        "Courtyard": COURTYARD,
        "Conspirator": CONSPIRATOR,
        "Courtier": COURTIER,
        "Baron": BARON,
        "Bridge": BRIDGE,
        "Diplomat": DIPLOMAT,
        "Duke": DUKE,
        "Harem": HAREM,
        "Nobles": NOBLES,
        "Ironworks": IRONWORKS,
        "Lurker": LURKER,
        "Masquerade": MASQUERADE,
        "Mill": MILL,
        "Mining Village": MINING_VILLAGE,
        "Minion": MINION,
        "Patrol": PATROL,
        "Pawn": PAWN,
        "Replace": REPLACE,
        "Secret Passage": SECRET_PASSAGE,
        "Shanty Town": SHANTY_TOWN,
        "Steward": STEWARD,
        "Swindler": SWINDLER,
        "Torturer": TORTURER,
        "Trading Post": TRADING_POST,
        "Upgrade": UPGRADE,
        "Wishing Well": WISHING_WELL,
    }
    if card in correspondences:
        return correspondences[card]()
    else:
        return CardInfo()
