# -*- coding: utf-8 -*-
from .CardInfo import CardInfo
from woodcutter.src.Card import *
from woodcutter.src.Action import Action


class PRIZE(CardInfo):
    names = ["Prize", "Prize", "Prize"]
    types = []
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class BAG_OF_GOLD(CardInfo):
    names = ["Bag of Gold", "Bags of Gold", "a Bag of Gold"]
    types = [Types.ACTION, Types.PRIZE]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class DIADEM(CardInfo):
    names = ["Diadem", "Diadems", "a Diadem"]
    types = [Types.TREASURE, Types.PRIZE]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class FAIRGROUNDS(CardInfo):
    names = ["Fairgrounds", "Fairgrounds", "a Fairgrounds"]
    types = [Types.VICTORY]
    cost = [6, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class FARMING_VILLAGE(CardInfo):
    names = ["Farming Village", "Farming Villages", "a Farming Village"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class FOLLOWERS(CardInfo):
    names = ["Followers", "Followers", "a Followers"]
    types = [Types.ACTION, Types.ATTACK, Types.PRIZE]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class FORTUNE_TELLER(CardInfo):
    names = ["Fortune Teller", "Fortune Tellers", "a Fortune Teller"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class HAMLET(CardInfo):
    names = ["Hamlet", "Hamlets", "a Hamlet"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class HARVEST(CardInfo):
    names = ["Harvest", "Harvests", "a Harvest"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class HORSE_TRADERS(CardInfo):
    names = ["Horse Traders", "Horse Traders", "a Horse Traders"]
    types = [Types.ACTION, Types.REACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class HORN_OF_PLENTY(CardInfo):
    names = ["Horn of Plenty", "Horns of Plenty", "a Horn of Plenty"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class HUNTING_PARTY(CardInfo):
    names = ["Hunting Party", "Hunting Parties", "a Hunting Party"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class JESTER(CardInfo):
    names = ["Jester", "Jesters", "a Jester"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class MENAGERIE(CardInfo):
    names = ["Menagerie", "Menageries", "a Menagerie"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class PRINCESS(CardInfo):
    names = ["Princess", "Princesses", "a Princess"]
    types = [Types.ACTION, Types.PRIZE]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class REMAKE(CardInfo):
    names = ["Remake", "Remakes", "a Remake"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TOURNAMENT(CardInfo):
    names = ["Tournament", "Tournaments", "a Tournament"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TRUSTY_STEED(CardInfo):
    names = ["Trusty Steed", "Trusty Steeds", "a Trusty Steed"]
    types = [Types.ACTION, Types.PRIZE]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class YOUNG_WITCH(CardInfo):
    names = ["Young Witch", "Young Witches", "a Young Witch"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state
