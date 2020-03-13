# HELP - I want to split this file up but I can't without breaking all
# the dependencies.
from copy import deepcopy
from .Utils import *
from .Enums import *
from .Cards import *
from .Card import *


class Action:
    name = "Unknown Action"

    def __init__(self):
        pass

    def __repr__(self):
        return self.name

    def act(self, state, log):
        return None


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
                    logLine.items, NeutralZones.SUPPLY, PlayerZones.DISCARD):
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

    def __init__(self, n):
        self.n = n
        self.name = "Draw {}".format(n)

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
            if log[state.logLine].pred == "DRAW":
                state.logLine += 1
                if not state.moveCards(logLine.items,
                                       PlayerZones.DECK,
                                       PlayerZones.HAND):
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
                if not state.moveCards(logLine.items,
                                       PlayerZones.DECK,
                                       PlayerZones.DECK):
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
            state.candidates = [actionPhase()] + state.turnStartEffects
            state.stack = [startOfTurn()]
            return state
        else:
            return None


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

            if state.actions > 0 and \
                    cardInfo.hasType(Types.ACTION):
                if state.moveCards([target], PlayerZones.HAND,
                                   PlayerZones.PLAY):
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
        state.candidates = [buyPhaseB(),
                            # repayDebt(), spendCoffers(),
                            treasurePlayNormal()]
        return state


class treasurePlayNormal(Action):
    name = "Play Treasure(s) from Hand"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]

        if logLine.pred in ["PLAY", "PLAY_TREASURES_FOR"]:
            if state.moveCards(
                    logLine.items, PlayerZones.HAND, PlayerZones.PLAY):

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
        state.candidates = [nightPhase(), repayDebt(),
                            buy(NeutralZones.SUPPLY, PlayerZones.DISCARD)]
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

            if cardInfo.hasType(Types.NIGHT) and \
                    state.zoneContains(target, PlayerZones.HAND):
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
        if state.moveAllCards(PlayerZones.HAND, PlayerZones.DISCARD) and \
                state.moveAllCards(PlayerZones.PLAY, PlayerZones.DISCARD):
            state.stack = [newTurn()]
            state.candidates = [drawN(5)]
            return state
        else:
            return None


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
                state.candidates = [onPlay(target)]
                return state
        return None


class replay(Action):
    name = "Replay"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]

        if logLine.pred in ["PLAY", "PLAY_AGAIN", "PLAY_THIRD",
                            "PLAY_AGAIN_CITADEL"]:
            target = logLine.items[0]
            state.logLine += 1

            state.candidates = [onPlay(target)]
            return state
        else:
            return None


class onPlay(Action):
    def __init__(self, target):
        self.name = "On Play {}".format(target)
        self.target = target

    def act(self, state, log):
        state = deepcopy(state)
        cardInfo = getCardInfo(self.target)
        if hasattr(cardInfo, "onPlay"):
            return cardInfo.onPlay(state, log)
        else:
            state.candidates = [state.stack.pop()]
            return state


class buy(Action):
    def __init__(self, src=NeutralZones.SUPPLY, dest=PlayerZones.DISCARD):
        self.name = "Buy from {} to {}".format(src, dest)
        self.src = src
        self.dest = dest

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player

        if logLine.pred == "BUY_AND_GAIN":
            state.logLine += 1
            if not state.moveCards(logLine.items, self.src, self.dest):
                return None
            for target in logLine.items:
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
    def __init__(self, src=NeutralZones.SUPPLY, dest=PlayerZones.DISCARD):
        self.name = "Gain from {} to {}".format(src, dest)
        self.src = src
        self.dest = dest

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player

        if logLine.pred == "GAIN":
            state.logLine += 1
            if not state.moveCards(logLine.items, self.src, self.dest):
                return None
            else:
                state.stack += [onGain(target) for target in logLine.items]

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

        if logLine.pred == "TOPDECK":
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
            if state.moveCards(logLine.items, PlayerZones.HAND,
                               PlayerZones.HAND):
                state.candidates = [state.stack.pop()]
                return state


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
            state.actions += amount
            state.logLine += 1
            state.candidates = [state.stack.pop()]
            return state
        elif logLine.pred in ["GETS_BUY", "GETS_BUY_FROM"]:
            state.actions += 1
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


class forceEnd(Action):
    name = "Win"

    def act(self, state, log):
        state = deepcopy(state)
        state.logLine += 900
        state.candidates = [forceEnd()]
        return state


class CardInfo:
    names = ["Back", "Backs", "a Back"]
    types = []
    cost = [0, 0, 0]

    def hasType(self, cardType):
        return cardType in self.types

    def onBuy(self, state, log):
        state = deepcopy(state)
        state.coins -= min(0, self.cost[0] - state.reductions)
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

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.candidates = [state.stack.pop()]
        state.coins += 1
        return state


class SILVER(CardInfo):
    names = ["Silver", "Silvers", "a Silver"]
    types = [Types.TREASURE]
    cost = [3, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.candidates = [state.stack.pop()]
        state.coins += 2
        return state


class GOLD(CardInfo):
    names = ["Gold", "Golds", "a Gold"]
    types = [Types.TREASURE]
    cost = [6, 0, 0]

    def onPlay(self, state, log):
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

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [topdeck(),
                        maybe(gain(NeutralZones.SUPPLY, PlayerZones.HAND))]
        state.candidates = [state.stack.pop()]
        return state


class BANDIT(CardInfo):
    names = ["Bandit", "Bandits", "a Bandit"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [maybe(discard(PlayerZones.DECK, PlayerZones.DISCARD)),
                        maybe(trash(PlayerZones.DECK, NeutralZones.TRASH)),
                        maybe(revealN(2)),
                        maybe(gain()),
                        reactToAttack()]
        state.candidates = [state.stack.pop()]
        return state


class BUREAUCRAT(CardInfo):
    names = ["Bureaucrat", "Bureaucrats", "a Bureaucrat"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [4, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [maybe(topdeck()),
                        maybe(revealHand()),
                        maybe(gain(NeutralZones.SUPPLY, PlayerZones.DECK)),
                        reactToAttack()]
        state.candidates = [state.stack.pop()]
        return state


class CELLAR(CardInfo):
    names = ["Cellar", "Cellars", "a Cellar"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        if state.logLine < len(log) - 1:
            amount = len(log[state.logLine + 1].items)
        state.stack += [maybe(drawN(amount)),
                        maybe(discard()),
                        getAction()]
        state.candidates = [state.stack.pop()]
        return state


class CHAPEL(CardInfo):
    names = ["Chapel", "Chapels", "a Chapel"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [maybe(trash())]
        state.candidates = [state.stack.pop()]
        return state


class COUNCIL_ROOM(CardInfo):
    names = ["Council Room", "Council Rooms", "a Council Room"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [drawN(1), getBuy(), drawN(4)]
        state.candidates = [state.stack.pop()]
        return state


class FESTIVAL(CardInfo):
    names = ["Festival", "Festivals", "a Festival"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
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

    def onPlay(self, state, log):
        state = deepcopy(state)
        # For some reason harbinger looks at discard twice
        state.stack += [maybe(topdeck(PlayerZones.DISCARD, PlayerZones.DECK)),
                        maybe(lookAt()), maybe(lookAt()),
                        getAction(), drawN(1)]
        state.candidates = [state.stack.pop()]
        return state


class LABORATORY(CardInfo):
    names = ["Laboratory", "Laboratories", "a Laboratory"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [getAction(), drawN(2)]
        state.candidates = [state.stack.pop()]
        return state


class LIBRARY(CardInfo):
    names = ["Library", "Libraries", "a Library"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player

        handCount = state.zoneCount(PlayerZones.HAND)
        deckCount = state.zoneCount(PlayerZones.DECK) + \
            state.zoneCount(PlayerZones.DISCARD)

        if handCount >= 7 or deckCount == 0:
            state.candidates = [maybe(discard(PlayerZones.SET_ASIDE,
                                              PlayerZones.DISCARD))]
        else:
            state.stack += [onPlay("Library"), maybe(setAside()),
                            maybe(lookAt()), drawN(1)]
            state.candidates = [state.stack.pop()]

        return state


class MARKET(CardInfo):
    names = ["Market", "Markets", "a Market"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [getCoin(), getBuy(), getAction(), drawN(1)]
        state.candidates = [state.stack.pop()]
        return state


class MERCHANT(CardInfo):
    names = ["Merchant", "Merchants", "a Merchant"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [getAction(), drawN(1)]
        state.candidates = [state.stack.pop()]
        return state


class MILITIA(CardInfo):
    names = ["Militia", "Militias", "a Militia"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [4, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [maybe(discard()), getCoin(), reactToAttack()]
        state.candidates = [state.stack.pop()]
        return state


class MINE(CardInfo):
    names = ["Mine", "Mines", "a Mine"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [gain(NeutralZones.SUPPLY, PlayerZones.HAND),
                        trash()]
        state.candidates = [state.stack.pop()]
        return state


class MOAT(CardInfo):
    # The reaction aspect of moat is baked into every attack -
    # The 'attack' parts are all maybe-d.
    names = ["Moat", "Moats", "a Moat"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log):
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

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [maybe(getCoin()), maybe(trash())]
        state.candidates = [state.stack.pop()]
        return state


class POACHER(CardInfo):
    names = ["Poacher", "Poachers", "a Poacher"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [maybe(discard()), getCoin(), getAction(), drawN(1)]
        state.candidates = [state.stack.pop()]
        return state


class REMODEL(CardInfo):
    names = ["Remodel", "Remodels", "a Remodel"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [gain(), trash()]
        state.candidates = [state.stack.pop()]
        return state


class SENTRY(CardInfo):
    names = ["Sentry", "Sentries", "a Sentry"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [maybe(topdeck(PlayerZones.DECK, PlayerZones.DECK)),
                        maybe(discard(PlayerZones.DECK, PlayerZones.DECK)),
                        maybe(trash(PlayerZones.DECK, PlayerZones.DECK)),
                        maybe(lookAt()), getAction(), drawN(1)]
        state.candidates = [state.stack.pop()]
        return state


class SMITHY(CardInfo):
    names = ["Smithy", "Smithies", "a Smithy"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [drawN(3)]
        state.candidates = [state.stack.pop()]
        return state


class THRONE_ROOM(CardInfo):
    names = ["Throne Room", "Throne Rooms", "a Throne Room"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [replay(), play()]
        state.candidates = [state.stack.pop()]
        return state


class VASSAL(CardInfo):
    names = ["Vassal", "Vassals", "a Vassal"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [maybe(play(PlayerZones.DISCARD)),
                        maybe(discard(PlayerZones.DECK, PlayerZones.DISCARD)),
                        getCoin()]
        state.candidates = [state.stack.pop()]
        return state


class VILLAGE(CardInfo):
    names = ["Village", "Villages", "a Village"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [getAction(), drawN(1)]
        state.candidates = [state.stack.pop()]
        return state


class WITCH(CardInfo):
    names = ["Witch", "Witches", "a Witch"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [maybe(gain()), drawN(2), reactToAttack()]
        state.candidates = [state.stack.pop()]
        return state


class WORKSHOP(CardInfo):
    names = ["Workshop", "Workshops", "a Workshop"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [maybe(gain())]
        state.candidates = [state.stack.pop()]
        return state


class COURTYARD(CardInfo):
    names = ["Couryard", "Courtyards", "a Courtyard"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [maybe(topdeck()), drawN(3)]
        state.candidates = [state.stack.pop()]
        return state


class CONSPIRATOR(CardInfo):
    names = ["Conspirator", "Conspirators", "a Conspirator"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [maybe(getAction()), maybe(drawN(1)), getCoin()]
        state.candidates = [state.stack.pop()]
        return state


class COURTIER(CardInfo):
    names = ["Courtier", "Courtiers", "a Courtier"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [maybe(gain()), maybe(getCoin()), maybe(getBuy()),
                        maybe(getAction()), revealHand()]
        state.candidates = [state.stack.pop()]
        return state


class BARON(CardInfo):
    names = ["Baron", "Barons", "a Baron"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [maybe(gain()), maybe(getCoin()), maybe(getBuy()),
                        maybe(discard())]
        state.candidates = [state.stack.pop()]
        return state


class BRIDGE(CardInfo):
    names = ["Bridge", "Bridges", "a Bridge"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.reductions += 1
        state.stack += [getCoin(), getBuy()]
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
        "Workshop": WORKSHOP
    }
    if card in correspondences:
        return correspondences[card]()
    else:
        return CardInfo()
