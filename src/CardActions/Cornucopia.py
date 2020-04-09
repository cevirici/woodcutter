# -*- coding: utf-8 -*-
from copy import deepcopy
from .CardInfo import CardInfo
from woodcutter.src.Card import *
from woodcutter.src.Action import Action
from woodcutter.src.GenericActions import *


class PRIZE(CardInfo):
    names = ["Prize", "Prize", "Prize"]
    types = []
    cost = [0, 0, 0]


class BAG_OF_GOLD(CardInfo):
    names = ["Bag of Gold", "Bags of Gold", "a Bag of Gold"]
    types = [Types.ACTION, Types.PRIZE]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[hasCard("Gold", gain(PlayerZones.DECK))], [getAction()]]
        state.candidates = state.stack.pop()
        return state


class DIADEM(CardInfo):
    names = ["Diadem", "Diadems", "a Diadem"]
    types = [Types.TREASURE, Types.PRIZE]
    cost = [0, 0, 0]


class FAIRGROUNDS(CardInfo):
    names = ["Fairgrounds", "Fairgrounds", "a Fairgrounds"]
    types = [Types.VICTORY]
    cost = [6, 0, 0]


class FARMING_VILLAGE(CardInfo):
    names = ["Farming Village", "Farming Villages", "a Farming Village"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[seek()], [getAction()]]
        state.candidates = state.stack.pop()
        return state


class FOLLOWERS(CardInfo):
    names = ["Followers", "Followers", "a Followers"]
    types = [Types.ACTION, Types.ATTACK, Types.PRIZE]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            [maybe(discard())],
            [maybe(gain())],
            [hasCard("Estate", gain())],
            [drawN()],
            [reactToAttack()],
        ]
        state.candidates = state.stack.pop()
        return state


class FORTUNE_TELLER(CardInfo):
    names = ["Fortune Teller", "Fortune Tellers", "a Fortune Teller"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            [maybe(seek(topdeck(PlayerZones.DECK, PlayerZones.DECK)))],
            [getCoin()],
            [reactToAttack()],
        ]
        state.candidates = state.stack.pop()
        return state


class HAMLET(CardInfo):
    names = ["Hamlet", "Hamlets", "a Hamlet"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            [maybe(getBuy())],
            [maybe(discard())],
            [maybe(getAction())],
            [maybe(discard())],
            [getAction()],
            [drawN(1)],
        ]
        state.candidates = state.stack.pop()
        return state


class HARVEST(CardInfo):
    names = ["Harvest", "Harvests", "a Harvest"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            [maybe(discard(PlayerZones.DECK, PlayerZones.DISCARD))],
            [getCoin()],
            [revealN(4)],
        ]
        state.candidates = state.stack.pop()
        return state


class htDuration(Action):
    name = "Horse Traders Effect"

    def act(self, state, log):
        state = deepcopy(state)
        state.stack += [
            [putInHand(PlayerZones.SET_ASIDE, PlayerZones.HAND)],
            [drawN(1)],
        ]
        for d in state.flags:
            if d[1] == "Horse Traders":
                state.flags.remove(d)

        state.candidates = state.stack.pop()
        return state


class HORSE_TRADERS(CardInfo):
    names = ["Horse Traders", "Horse Traders", "a Horse Traders"]
    types = [Types.ACTION, Types.REACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[discard()], [getBuy()], [getCoin()]]
        state.candidates = state.stack.pop()
        return state

    def onReact(self, state, log):
        state = deepcopy(state)
        state.flags.append((FlagTypes.START_OF_TURN, "Horse Traders", htDuration))
        state.stack += [[setAside(PlayerZones.PLAY, PlayerZones.SET_ASIDE)]]
        state.candidates = state.stack.pop()
        return state


class HORN_OF_PLENTY(CardInfo):
    names = ["Horn of Plenty", "Horns of Plenty", "a Horn of Plenty"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[maybe(trash(PlayerZones.PLAY))], [gain()]]
        state.candidates = state.stack.pop()
        return state


class hpSeek(Action):
    name = "Hunting Party Seek"

    def act(self, state, log):
        state = deepcopy(state)
        handCount = state.zoneCount(PlayerZones.HAND)
        deckCount = state.zoneCount(PlayerZones.DECK)
        discardCount = state.zoneCount(PlayerZones.DISCARD)

        if handCount + deckCount > 0:
            if log[state.logLine].pred == "REVEAL":
                state.logLine += 1
            else:
                return None

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

        state.stack += [
            maybe(discard(PlayerZones.DECK, PlayerZones.DISCARD)),
            maybe(putInHand()),
        ]

        state.candidates = state.stack.pop()
        return state


class HUNTING_PARTY(CardInfo):
    names = ["Hunting Party", "Hunting Parties", "a Hunting Party"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[hpSeek()], [getAction()], [drawN(1)]]
        state.candidates = state.stack.pop()
        return state


class JESTER(CardInfo):
    names = ["Jester", "Jesters", "a Jester"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            [maybe(gain())],
            [maybe(discard(PlayerZones.DECK, PlayerZones.DISCARD))],
            [getCoin()],
            [reactToAttack()],
        ]
        state.candidates = state.stack.pop()
        return state


class MENAGERIE(CardInfo):
    names = ["Menagerie", "Menageries", "a Menagerie"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[drawN(1), drawN(3)], [revealHand()], [getAction()]]
        state.candidates = state.stack.pop()
        return state


class PRINCESS(CardInfo):
    names = ["Princess", "Princesses", "a Princess"]
    types = [Types.ACTION, Types.PRIZE]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[getBuy()]]
        state.candidates = state.stack.pop()
        return state

    def onEnterPlay(self, state, cardIndex):
        state.reductions.append((None, 2, cardIndex))

    def onLeavePlay(self, state, cardIndex):
        for r in state.reductions:
            if r[2] == cardIndex:
                state.reductions.remove(r)


class REMAKE(CardInfo):
    names = ["Remake", "Remakes", "a Remake"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            [maybe(gain())],
            [hasCards(trash())],
            [maybe(gain())],
            [hasCards(trash())],
        ]
        state.candidates = state.stack.pop()
        return state


class TOURNAMENT(CardInfo):
    names = ["Tournament", "Tournaments", "a Tournament"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[maybe(getCoin())], [maybe(drawN(1))], [maybe(gain())]]
        state.stack += [[maybe(revealHand())] for p in range(PLAYER_COUNT)]
        state.stack += [[getAction()]]
        state.candidates = state.stack.pop()
        return state


class TRUSTY_STEED(CardInfo):
    names = ["Trusty Steed", "Trusty Steeds", "a Trusty Steed"]
    types = [Types.ACTION, Types.PRIZE]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            [maybe(chancellor())],
            [maybe(gain())],
            [maybe(getCoin())],
            [maybe(getAction())],
            [maybe(drawN(2))],
        ]
        state.candidates = state.stack.pop()
        return state


class YOUNG_WITCH(CardInfo):
    names = ["Young Witch", "Young Witches", "a Young Witch"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            [maybe(gain())],
            [maybe(revealHand())],
            [hasCards(discard())],
            [drawN(2)],
            [reactToAttack()],
        ]
        state.candidates = state.stack.pop()
        return state
