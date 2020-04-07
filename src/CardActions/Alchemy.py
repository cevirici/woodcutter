# -*- coding: utf-8 -*-
from .CardInfo import CardInfo
from woodcutter.src.Card import *
from woodcutter.src.Action import Action


class ALCHEMIST(CardInfo):
    names = ["Alchemist", "Alchemists", "an Alchemist"]
    types = [Types.ACTION]
    cost = [3, 1, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class APOTHECARY(CardInfo):
    names = ["Apothecary", "Apothecaries", "an Apothecary"]
    types = [Types.ACTION]
    cost = [2, 1, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class APPRENTICE(CardInfo):
    names = ["Apprentice", "Apprentices", "an Apprentice"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class FAMILIAR(CardInfo):
    names = ["Familiar", "Familiars", "a Familiar"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [3, 1, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class GOLEM(CardInfo):
    names = ["Golem", "Golems", "a Golem"]
    types = [Types.ACTION]
    cost = [4, 1, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class HERBALIST(CardInfo):
    names = ["Herbalist", "Herbalists", "a Herbalist"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class PHILOSOPHERS_STONE(CardInfo):
    names = ["Philosopher's Stone", "Philosopher's Stones", "a Philosopher's Stone"]
    types = [Types.TREASURE]
    cost = [3, 1, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class POSSESSION(CardInfo):
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
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SCRYING_POOL(CardInfo):
    names = ["Scrying Pool", "Scrying Pools", "a Scrying Pool"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [2, 1, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TRANSMUTE(CardInfo):
    names = ["Transmute", "Transmutes", "a Transmute"]
    types = [Types.ACTION]
    cost = [0, 1, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class UNIVERSITY(CardInfo):
    names = ["University", "Universities", "a University"]
    types = [Types.ACTION]
    cost = [2, 1, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class VINEYARD(CardInfo):
    names = ["Vineyard", "Vineyards", "a Vineyard"]
    types = [Types.VICTORY]
    cost = [0, 1, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state
