# -*- coding: utf-8 -*-
from copy import deepcopy
from .Utils import *
from .Enums import *
from .Card import *
from .CardActions import *
from .Action import *

# Conditionals and other stuff


class nothing(Action):
    name = "Do Nothing"

    def act(self, state, log):
        state = deepcopy(state)
        state.candidates = state.stack.pop() if state.stack else []
        return state


class maybe(Action):
    def __init__(self, action):
        self.name = "Maybe {}".format(action.name)
        self.action = action

    def act(self, state, log):
        state = deepcopy(state)
        state.candidates = [nothing(), self.action]
        return state


class conditionally(Action):
    def __init__(self, condition, action):
        self.name = "Conditionally {}".format(action.name)
        self.action = action
        self.condition = condition

    def act(self, state, log):
        state = deepcopy(state)
        if self.condition(state, log):
            state.candidates = [self.action]
        else:
            state.candidates = state.stack.pop()
        return state


def hasCards(action):
    # Conditional upon the player having cards in hand
    def hasCardsCondition(state, log):
        return state.zoneCount(PlayerZones.HAND) > 0

    return conditionally(hasCardsCondition, action)


def hasSupply(action):
    def hasSupplyCondition(state, log):
        return state.zoneCount(NeutralZones.SUPPLY) > 0

    return conditionally(hasSupplyCondition, action)


def hasCard(cardName, action):
    def hasCardCondition(state, log):
        for card in state.zones[NeutralZones.SUPPLY]:
            if card.name == cardName:
                return True
        return False

    return conditionally(hasSupplyCondition, action)


# Pregame


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


class gameStartDraw(Action):
    name = "Initial Draw"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player
        state.stack = [[newTurn()]]
        state.stack += [[drawN(5)] for i in range(PLAYER_COUNT)]
        state.candidates = state.stack.pop()
        return state


# Normal Turn Loop


class newTurn(Action):
    name = "New Turn"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        if logLine.pred == "NEW_TURN":
            state.player = logLine.player
            state.logLine += 1
            state.candidates = [actionPhase(), startTurn()]

            state.actions, state.buys, state.coins = (1, 1, 0)
            state.potions, state.reductions = (0, [])
            return state


class startTurn(Action):
    name = "Turn Start Phase"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        if logLine.pred == "STARTS_TURN":
            state.player = logLine.player
            state.logLine += 1
            state.candidates = [startOfTurn()]
            return state


class startOfTurn(Action):
    name = "Turn Start Phase"

    def act(self, state, log):
        state = deepcopy(state)
        state.candidates = [actionPhase()]
        state.candidates += [d[2] for d in state.flags if d[0] == "STARTS_TURN"]
        state.stack = [[startOfTurn()]]
        return state


class actionPhase(Action):
    name = "Action Phase"

    def act(self, state, log):
        state = deepcopy(state)
        state.player = log[state.logLine].player
        state.candidates = [buyPhaseA(), actionPlayNormal()]
        state.stack = [[actionPhase()]]
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
                card = state.moveCards([target], PlayerZones.HAND, PlayerZones.PLAY)
                if card:
                    state.actions -= 1
                    card = card[0]
                    state.candidates = [onPlay(card)]
                    return state


class buyPhaseA(Action):
    name = "Buy Phase A"

    def act(self, state, log):
        state = deepcopy(state)
        state.player = log[state.logLine].player
        state.stack = [[buyPhaseA()]]
        state.candidates = [
            buyPhaseB(),
            repayDebt(),
            # spendCoffers(),
            treasurePlayNormal(),
        ]
        return state


class treasurePlayNormal(Action):
    name = "Play Treasure(s) from Hand"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]

        if logLine.pred in ["PLAY", "PLAY_TREASURES_FOR"]:
            if logLine.pred == "PLAY_TREASURES_FOR":
                state.coins += int(logLine.args[0])

            cards = state.moveCards(logLine.items, PlayerZones.HAND, PlayerZones.PLAY)
            if cards:
                for card in cards:
                    if not getCardInfo(card.name).hasType(Types.TREASURE):
                        return None
                    state.stack.append([onPlay(card)])
                state.logLine += 1
                state.candidates = state.stack.pop()
                return state


class buyPhaseB(Action):
    name = "Buy Phase B"

    def act(self, state, log):
        state = deepcopy(state)
        state.player = log[state.logLine].player
        state.stack = [[buyPhaseB()]]
        state.candidates = [nightPhase(), repayDebt(), buy()]
        return state


class repayDebt(Action):
    name = "Repay Debt"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]

        if logLine.pred == "REPAYS_DEBT":
            amount = int(logLine.args[1])
        elif logLine.pred == "REPAYS_SOME_DEBT":
            amount = int(logLine.args[0])
        else:
            return None

        if state.coins < amount:
            return None
        state.coins -= amount
        state.debt[state.player] -= amount
        return state


class nightPhase(Action):
    name = "Night Phase"

    def act(self, state, log):
        state = deepcopy(state)
        state.player = log[state.logLine].player
        state.stack = [[nightPhase()]]
        state.candidates = [cleanupPhase(), nightPlayNormal()]
        return state


class nightPlayNormal(Action):
    name = "Play Night from Hand"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]

        if logLine.pred == "PLAY" and len(logLine.items) == 1:
            state.logLine += 1
            target = logLine.items[0]
            cardInfo = getCardInfo(target)

            if cardInfo.hasType(Types.NIGHT) and state.zoneContains(
                target, PlayerZones.HAND
            ):
                card = state.moveCards([target], PlayerZones.HAND, PlayerZones.PLAY)
                state.candidates = [onPlay(card[0])]
                return state


class cleanupPhase(Action):
    name = "Cleanup Phase"

    def act(self, state, log):
        state = deepcopy(state)
        state.player = log[state.logLine].player
        state.stack = [[cleanupPhase()]]
        state.candidates = [cleanupDraw()]
        state.candidates += [d[2] for d in state.flags if d[0] == "CLEANUP"]
        return state


class cleanupDraw(Action):
    name = "Cleanup Draw"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player

        remaining = []
        for d in state.flags:
            if d[0] != "CLEANUP":
                remaining.append(d)
        state.flags = remaining

        # Discarding stuff from play / hands
        state.moveAllCards(PlayerZones.HAND, PlayerZones.DISCARD)

        remaining = []
        for card in state.zones[PlayerZones.PLAY][state.player]:
            if card.stayingOut != 0:
                card.stayingOut -= 1
                remaining.append(card)
            elif [s for s in card.slaves if s.stayingOut != 0]:
                remaining.append(card)
            else:
                state.zones[PlayerZones.DISCARD][state.player].append(card)
                card.move(PlayerZones.DISCARD)
        state.zones[PlayerZones.PLAY][state.player] = remaining

        state.stack = [[newTurn()]]
        state.candidates = [drawN(5)]
        return state


# Standard actions


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
                state.candidates = state.stack.pop()
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
            state.stack.append([self])
            return state
        elif deckCount > 0:
            if log[state.logLine].pred == "DRAW":
                state.logLine += 1
                if not state.moveCards(
                    logLine.items, PlayerZones.DECK, PlayerZones.HAND
                ):
                    return None
        state.candidates = state.stack.pop()
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
            state.stack.append([self])
            return state
        elif deckCount > 0:
            if log[state.logLine].pred == "REVEAL":
                state.logLine += 1
                if not state.moveCards(
                    logLine.items, PlayerZones.DECK, PlayerZones.DECK
                ):
                    return None
        state.candidates = state.stack.pop()
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

            card = state.moveCards([target], self.src, PlayerZones.PLAY)
            if card:
                state.stack.append([onPlay(card[0])])
                state.candidates = state.stack.pop()
                return state


class replay(Action):
    name = "Replay"

    def __init__(self, card):
        self.card = card

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]

        if logLine.pred in ["PLAY", "PLAY_AGAIN", "PLAY_THIRD", "PLAY_AGAIN_CITADEL"]:
            state.logLine += 1

            state.candidates = [onPlay(self.card)]
            return state


class onPlay(Action):
    def __init__(self, card):
        self.name = "On Play {}".format(card.name)
        self.card = card

    def act(self, state, log):
        state = deepcopy(state)
        cardInfo = getCardInfo(self.card.name)
        if hasattr(cardInfo, "onPlay"):
            return cardInfo.onPlay(state, log, self.card.index)
        else:
            state.candidates = state.stack.pop()
            return state


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
            state.candidates = state.stack.pop()
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

                state.stack += [[onGain(target)], [onBuy(target)]]

            state.candidates = state.stack.pop()
            return state

        elif logLine.pred == "BUY":
            state.logLine += 1
            for target in logLine.items:
                state.stack += [[gain(self.src, self.dest)], [onBuy(target)]]

            state.candidates = state.stack.pop()
            return state

        return None


class onBuy(Action):
    def __init__(self, target):
        self.name = "On Buy {}".format(target)
        self.target = target

    def act(self, state, log):
        state = deepcopy(state)
        cardInfo = getCardInfo(self.target)

        for pile in state.piles:
            if self.target in pile:
                if pile.embargoTokens > 0:
                    state.stack += [[conditionally(hasCard("Curse"), gain())]]
                break

        if hasattr(cardInfo, "onBuy"):
            return cardInfo.onBuy(state, log)
        else:
            state.candidates = state.stack.pop()
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

                state.stack.append([onGain(target)])

            state.candidates = state.stack.pop()
            return state


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
            state.candidates = state.stack.pop()
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
            for target in logLine.items:
                if not state.moveCards([target], self.src, self.dest):
                    return None

                state.stack.append([onDiscard(target)])

            state.candidates = state.stack.pop()
            return state


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
            state.candidates = state.stack.pop()
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
                state.stack += [[onTrash(target)] for target in logLine.items]

                state.candidates = state.stack.pop()
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
            state.candidates = state.stack.pop()
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
                state.stack += [[onTopdeck(target)] for target in logLine.items]

                state.candidates = state.stack.pop()
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
            state.candidates = state.stack.pop()
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
                state.candidates = state.stack.pop()
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
                state.candidates = state.stack.pop()
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
                state.candidates = state.stack.pop()
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
            state.candidates = state.stack.pop()
            return state
        elif logLine.pred in ["GETS_ACTION", "GETS_ACTION_FROM"]:
            state.actions += 1
            state.logLine += 1
            state.candidates = state.stack.pop()
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
            state.candidates = state.stack.pop()
            return state
        elif logLine.pred in ["GETS_BUY", "GETS_BUY_FROM"]:
            state.buys += 1
            state.logLine += 1
            state.candidates = state.stack.pop()
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
            state.candidates = state.stack.pop()
            return state
        elif logLine.pred in ["GETS_COIN", "GETS_COIN_FROM"]:
            state.coins += 1
            state.logLine += 1
            state.candidates = state.stack.pop()
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
            state.candidates = state.stack.pop()
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
            state.candidates = state.stack.pop()
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
            state.stack.append([self])
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
        state.candidates = state.stack.pop()
        return state


class reactToAttack(Action):
    name = "React to Attack"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]

        if logLine.pred == "REACTS_WITH":
            state.logLine += 1
            state.stack.append([self])
            state.stack += [[onReact(target)] for target in logLine.items]

        state.candidates = state.stack.pop()
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
            state.candidates = state.stack.pop()
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
            prevPlayer = (state.player - 1) % PLAYER_COUNT

            if not state.moveCards(
                [target], PlayerZones.HAND, PlayerZones.HAND, prevPlayer, state.player
            ):
                return None

            state.candidates = state.stack.pop()
            return state
        return None


class wishRight(Action):
    name = "Wish Success"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player

        deckCount = state.zoneCount(PlayerZones.DECK)
        discardCount = state.zoneCount(PlayerZones.DISCARD)

        if deckCount == 0 and discardCount > 0:
            # Shuffle then go again
            state.candidates = [shuffle()]
            state.stack.append([self])
            return state
        else:
            if logLine.pred == "WISH_CORRECT":
                state.logLine += 1
                if not state.moveCards(
                    [logLine.args[0]], PlayerZones.DECK, PlayerZones.HAND
                ):
                    return None
                else:
                    state.candidates = state.stack.pop()
                    return state
            return None


class wishWrong(Action):
    name = "Wish Wrong"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player

        deckCount = state.zoneCount(PlayerZones.DECK)
        discardCount = state.zoneCount(PlayerZones.DISCARD)

        if deckCount == 0 and discardCount > 0:
            # Shuffle then go again
            state.candidates = [shuffle()]
            state.stack.append([self])
            return state
        else:
            if logLine.pred == "WISH_WRONG":
                state.logLine += 1
                if not state.moveCards(
                    [logLine.args[1]], PlayerZones.DECK, PlayerZones.DECK
                ):
                    return None
                else:
                    state.candidates = state.stack.pop()
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

            state.candidates = state.stack.pop()
            return state
        return None


class trashAttack(Action):
    name = "Trash Attack"

    def __init__(self, count=2):
        self.count = count

    def act(self, state, log):
        state = deepcopy(state)
        state.stack += [
            [maybe(discard(PlayerZones.DECK, PlayerZones.DISCARD))],
            [trash(PlayerZones.DECK, NeutralZones.TRASH)],
            [revealN(self.count)],
        ]
        state.candidates = state.stack.pop()
        return state


class scry(Action):
    name = "Scry"

    def act(self, state, log):
        state = deepcopy(state)
        state.stack += [
            [
                discard(PlayerZones.DECK, PlayerZones.DISCARD),
                topdeck(PlayerZones.DECK, PlayerZones.DECK),
            ],
            [revealN(1)],
        ]
        state.candidates = state.stack.pop()
        return state


class forceEnd(Action):
    name = "Win"

    def act(self, state, log):
        state = deepcopy(state)
        state.logLine += 900
        state.candidates = [forceEnd()]
        return state


from .CardActions.GetCardInfo import getCardInfo
