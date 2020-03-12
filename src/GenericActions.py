# Actions associated with a predicate
from copy import deepcopy
from .Utils import *
from .Cards import *


class Action:
    name = "Unknown Action"

    def __init__(self):
        pass

    def __repr__(self):
        return self.name

    def act(self, state, log):
        return None


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
        state.resolutionStack += [gameStartDraw()]
        state.candidates = [endGameStart(), drawN(5)]
        return state


class shuffle(Action):
    name = "Shuffle"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player
        if logLine.pred == "SHUFFLES":
            state.moveAllCards(PlayerZones.DISCARD, PlayerZones.DECK)
            if state.resolutionStack:
                state.logLine += 1
                state.candidates = [state.resolutionStack.pop()]
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
            state.resolutionStack += [self]
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
        state.candidates = [state.resolutionStack.pop()]
        return state


class endGameStart(Action):
    name = "Begin Game"

    def act(self, state, log):
        state = deepcopy(state)
        state.resolutionStack.pop()
        state.candidates = [newTurn()]
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
            # state.candidates = [forceEnd()]

            state.actions = 1
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
            state.resolutionStack = [startOfTurn()]
            return state
        else:
            return None


class actionPhase(Action):
    name = "Action Phase"

    def act(self, state, log):
        state = deepcopy(state)
        state.resolutionStack = [actionPhase()]
        state.candidates = [buyPhaseA(), actionPlayNormal()]

        return state


class actionPlayNormal(Action):
    name = "Play Action from Hand"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]

        if logLine.pred == "PLAY" and len(logLine.items) == 1:
            target = logLine.items[0]
            if state.actions > 0 and \
                    isAction(target) and \
                    state.zoneContains(target, PlayerZones.HAND):
                state.actions -= 1
                state.moveCards([target], PlayerZones.HAND, PlayerZones.PLAY)
                state.candidates = [playAction(target)]
                return state
            else:
                return None
        else:
            return None


class playAction(Action):
    def __init__(self, target):
        self.name = "Play " + target

    def act(self, state, log):
        return None


class buyPhaseA(Action):
    name = "Buy Phase A"

    def act(self, state, log):
        state = deepcopy(state)
        state.resolutionStack = [buyPhaseA()]
        state.candidates = [buyPhaseB(), 
                            # repayDebt(), spendCoffers(),
                            treasurePlayNormal()]
        return state


class treasurePlayNormal(Action):
    name = "Play Treasure from Hand"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]

        if logLine.pred in ["PLAY", "PLAY_TREASURES_FOR"]:
            if state.moveCards(
                    logLine.items, PlayerZones.HAND, PlayerZones.PLAY):

                for target in logLine.items:
                    if not isTreasure(target):
                        return None
                    state.resolutionStack += [playTreasure(target)]
                state.logLine += 1
                state.candidates = [state.resolutionStack.pop()]
                return state
            else:
                return None
        else:
            return None


class playTreasure(Action):
    def __init__(self, target):
        self.name = "Play " + target

    def act(self, state, log):
        state = deepcopy(state)
        state.candidates = [state.resolutionStack.pop()]
        return state


class buyPhaseB(Action):
    name = "Buy Phase B"

    def act(self, state, log):
        state = deepcopy(state)
        state.resolutionStack = [buyPhaseB()]
        # state.candidates = [nightPhase(), repayDebt(), buyNormal()]
        state.candidates = [forceEnd()]
        return state


# class nightPhase(Action):
#     name = "Night Phase"

#     def act(self, state, log):
#         state = deepcopy(state)
#         state.resolutionStack = [nightPhase()]
#         # state.candidates = [cleanupPhase(), nightPlayNormal()]
#         return state


# class cleanupPhase(Action):
#     name = "Cleanup Phase"

#     def act(self, state, log):
#         state = deepcopy(state)
#         state.resolutionStack = [cleanupPhase()]
#         # state.candidates = [drawNextHand()] + self.cleanupEffects
#         return state


class forceEnd(Action):
    name = "Win"

    def act(self, state, log):
        state = deepcopy(state)
        state.logLine += 900
        return state
