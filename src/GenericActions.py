# Generic actions
from copy import deepcopy
from .Utils import *


def startGame(state, log):
    # Presumes correctness.
    state = deepcopy(state)
    state.logLine += 1
    state.candidates = [startDecks]
    return state


def startDecks(state, log):
    # Presumes correctness.
    state = deepcopy(state)
    state.player = getOwner(log[state.logLine])

    items = getItems(log[state.logLine])
    src = Cards[items.keys()[0]].initialZone
    state.moveCards(items, src, PlayerZones.DISCARD)
    state.logLine += 1
    if getPred(log[state.logLine]) == 23:
        state.candidates = [startDecks]
    else:
        state.candidates = [drawN(5)]
        state.resolutionStack += [newTurn, drawN(5)]
    return state


def popResolutionStack(state, log):
    event = state.resolutionStack.pop()
    return event(state, log)


def drawN(n):
    # n should be positive
    def outFn(state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = getOwner(logLine)
        deckCount = state.zoneCount(PlayerZones.DECK)
        if deckCount < n:
            if deckCount > 0:
                if getPred(logLine != 8):
                    raise LogMismatch
                state.moveCards(getItems(logLine),
                                PlayerZones.DECK, PlayerZones.HAND)
                state.logLine += 1

            if getPred(logLine != 28):
                raise LogMismatch
            items = state.zones[PlayerZones.DISCARD][state.player][0].cards
            state.moveCards(items, PlayerZones.DISCARD, PlayerZones.DECK)
            state.logLine += 1

        if state.zoneCount(PlayerZones.DECK) > 0:
            if getPred(logLine != 8):
                raise LogMismatch
            state.moveCards(getItems(logLine),
                            PlayerZones.DECK, PlayerZones.HAND)
            state.logLine += 1

        return popResolutionStack(state, log)
    return outFn


def newTurn(state, log):
    state = deepcopy(state)
    state.logLine += 900
    return state
