# -*- coding: utf-8 -*-
from copy import deepcopy
from .CardInfo import CardInfo
from woodcutter.src.Card import *
from woodcutter.src.Action import Action
from woodcutter.src.GenericActions import *


class alchemistCleanup(Action):
    name = "Alchemist Cleanup"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.logLine += 1

        if logLine.pred == "TOPDECK":
            amount = len(logLine.items)
            if logLine.items[0] != "Alchemist":
                return None
            if not state.moveCards(logLine.items, PlayerZones.PLAY, PlayerZones.DECK):
                return None

            i = 0
            remaining = []
            for d in state.flags:
                if d[1] == "Alchemist" and i < amount:
                    i += 1
                else:
                    remaining.append(d)
            state.flags = remaining

            if i < amount:
                return None
            else:
                state.candidates = state.stack.pop()
                return state
        else:
            return None


class ALCHEMIST(CardInfo):
    names = ["Alchemist", "Alchemists", "an Alchemist"]
    types = [Types.ACTION]
    cost = [3, 1, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.flags.append(("CLEANUP", "Alchemist", alchemistCleanup()))
        state.stack += [[getAction()], [drawN(2)]]
        state.candidates = state.stack.pop()
        return state


class APOTHECARY(CardInfo):
    names = ["Apothecary", "Apothecaries", "an Apothecary"]
    types = [Types.ACTION]
    cost = [2, 1, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            [maybe(topdeck(PlayerZones.DECK))],
            [maybe(putInHand())],
            [revealN(4)],
            [getAction()],
            [drawN(1)],
        ]
        state.candidates = state.stack.pop()
        return state


class APPRENTICE(CardInfo):
    names = ["Apprentice", "Apprentices", "an Apprentice"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            [maybe(drawN(0))],
            [maybe(shuffle())],
            [hasCards(trash())],
            [getAction()],
        ]
        state.candidates = state.stack.pop()
        return state


class FAMILIAR(CardInfo):
    names = ["Familiar", "Familiars", "a Familiar"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [3, 1, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[maybe(gain())], [getAction()], [drawN(1)], [reactToAttack()]]
        state.candidates = state.stack.pop()
        return state


class GOLEM(CardInfo):
    names = ["Golem", "Golems", "a Golem"]
    types = [Types.ACTION]
    cost = [4, 1, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        targets = []
        deckCount = state.zoneCount(PlayerZones.DECK)
        discardCount = state.zoneCount(PlayerZones.DISCARD)

        if deckCount > 0:
            if log[state.logLine].pred == "REVEAL":
                state.logLine += 1
                if not state.moveCards(
                    logLine.items, PlayerZones.DECK, PlayerZones.DECK
                ):
                    return None

                for card in logLine.items:
                    if card != "Golem":
                        cardInfo = getCardInfo(card)
                        if Types.ACTION in cardInfo.types:
                            targets.append(card)

            else:
                return None

        if len(targets) < 2:
            if discardCount > 0:
                if log[state.logLine].pred == "SHUFFLES":
                    state.moveAllCards(PlayerZones.DISCARD, PlayerZones.DECK)
                    state.logLine += 1

                if log[state.logLine].pred == "REVEAL":
                    state.logLine += 1
                    if not state.moveCards(
                        logLine.items, PlayerZones.DECK, PlayerZones.DECK
                    ):
                        return None

                    for card in logLine.items:
                        if card != "Golem":
                            cardInfo = getCardInfo(card)
                            if Types.ACTION in cardInfo.types:
                                targets.append(card)

                else:
                    return None

        if not state.moveCards(targets, PlayerZones.DECK, PlayerZones.SET_ASIDE):
            return None

        state.stack += [[play(PlayerZones.SET_ASIDE)] for t in targets]
        state.stack += [[maybe(discard(PlayerZones.DECK, PlayerZones.DISCARD))]]
        state.candidates = state.stack.pop()
        return state


class herbalistCleanup(Action):
    name = "Herbalist Cleanup"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.logLine += 1

        if logLine.pred == "TOPDECK":
            amount = len(logLine.items)
            for card in logLine.items:
                if Types.TREASURE not in getCardInfo(card).types:
                    return None
            if not state.moveCards(logLine.items, PlayerZones.PLAY, PlayerZones.DECK):
                return None

            i = 0
            remaining = []
            for d in state.flags:
                if d[1] == "Herbalist" and i < amount:
                    i += 1
                else:
                    remaining.append(d)
            state.flags = remaining

            if i < amount:
                return None
            else:
                state.candidates = state.stack.pop()
                return state
        else:
            return None


class HERBALIST(CardInfo):
    names = ["Herbalist", "Herbalists", "a Herbalist"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.flags.append(("CLEANUP", "Herbalist", herbalistCleanup()))
        state.stack += [[getCoin()], [getBuy()]]
        state.candidates = state.stack.pop()
        return state


class PHILOSOPHERS_STONE(CardInfo):
    names = ["Philosopher's Stone", "Philosopher's Stones", "a Philosopher's Stone"]
    types = [Types.TREASURE]
    cost = [3, 1, 0]


class POSSESSION(CardInfo):
    # THIS IS FUCKED.
    names = ["Possession", "Possessions", "a Possession"]
    types = [Types.ACTION]
    cost = [6, 1, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class POTION(CardInfo):
    names = ["Potion", "Potions", "a Potion"]
    types = [Types.TREASURE]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.potions += 1
        state.candidates = state.stack.pop()
        return state


class poolDraw(Action):
    name = "Scrying Pool Draw"

    def act(self, state, log):
        state = deepcopy(state)
        deckCount = state.zoneCount(PlayerZones.DECK)
        discardCount = state.zoneCount(PlayerZones.DISCARD)
        keepDrawing = True

        if deckCount > 0:
            if log[state.logLine].pred == "REVEAL":
                state.logLine += 1
                if not state.moveCards(
                    logLine.items, PlayerZones.DECK, PlayerZones.DECK
                ):
                    return None

                for card in logLine.items:
                    cardInfo = getCardInfo(card)
                    if Types.ACTION not in cardInfo.types:
                        keepDrawing = False

            else:
                return None

        if keepDrawing:
            if discardCount > 0:
                if log[state.logLine].pred == "SHUFFLES":
                    state.moveAllCards(PlayerZones.DISCARD, PlayerZones.DECK)
                    state.logLine += 1

                if log[state.logLine].pred == "REVEAL":
                    state.logLine += 1
                    if not state.moveCards(
                        logLine.items, PlayerZones.DECK, PlayerZones.DECK
                    ):
                        return None
                else:
                    return None

        if deckCount > 0 or discardCount > 0:
            state.stack.append([putInHand()])

        state.candidates = state.stack.pop()
        return state


class SCRYING_POOL(CardInfo):
    names = ["Scrying Pool", "Scrying Pools", "a Scrying Pool"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [2, 1, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [poolDraw()]
        state.stack += [maybe(scry()) for p in range(PLAYER_COUNT)]
        state.stack += [[getAction()], [reactToAttack()]]
        state.candidates = state.stack.pop()
        return state


class TRANSMUTE(CardInfo):
    names = ["Transmute", "Transmutes", "a Transmute"]
    types = [Types.ACTION]
    cost = [0, 1, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            [maybe(gain())],
            [maybe(gain())],
            [maybe(gain())],
            [hasCards(trash())],
        ]
        state.candidates = state.stack.pop()
        return state


class UNIVERSITY(CardInfo):
    names = ["University", "Universities", "a University"]
    types = [Types.ACTION]
    cost = [2, 1, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[maybe(gain())], [getAction()]]
        state.candidates = state.stack.pop()
        return state


class VINEYARD(CardInfo):
    names = ["Vineyard", "Vineyards", "a Vineyard"]
    types = [Types.VICTORY]
    cost = [0, 1, 0]
