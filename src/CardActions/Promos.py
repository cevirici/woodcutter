# -*- coding: utf-8 -*-
from .CardInfo import CardInfo
from woodcutter.src.Card import *
from woodcutter.src.Action import Action


class SAUNA(CardInfo):
    names = ["Sauna", "Saunas", "a Sauna"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class AVANTO(CardInfo):
    names = ["Avanto", "Avantos", "an Avanto"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class BLACK_MARKET(CardInfo):
    names = ["Black Market", "Black Markets", "a Black Market"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class ENVOY(CardInfo):
    names = ["Envoy", "Envoys", "an Envoy"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class GOVERNOR(CardInfo):
    names = ["Governor", "Governors", "a Governor"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class PRINCE(CardInfo):
    names = ["Prince", "Princes", "a Prince"]
    types = [Types.ACTION]
    cost = [8, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class STASH(CardInfo):
    names = ["Stash", "Stashes", "a Stash"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SUMMON(CardInfo):
    names = ["Summon", "Summons", "a Summon"]
    types = [Types.EVENT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WALLED_VILLAGE(CardInfo):
    names = ["Walled Village", "Walled Villages", "a Walled Village"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class BLACK_MARKET_DECK(CardInfo):
    names = ["Black Market Deck", "Black Market Decks", "a Black Market Deck"]
    types = []
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class DISMANTLE(CardInfo):
    names = ["Dismantle", "Dismantles", "a Dismantle"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CAPTAIN(CardInfo):
    names = ["Captain", "Captains", "a Captain"]
    types = [Types.ACTION, Types.DURATION, Types.COMMAND]
    cost = [6, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CHURCH(CardInfo):
    names = ["Church", "Churches", "a Church"]
    types = [Types.ACTION, Types.DURATION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state
