# -*- coding: utf-8 -*-
from .CardInfo import CardInfo
from woodcutter.src.Card import *
from woodcutter.src.Action import Action


class BORDER_VILLAGE(CardInfo):
    names = ["Border Village", "Border Villages", "a Border Village"]
    types = [Types.ACTION]
    cost = [6, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CACHE(CardInfo):
    names = ["Cache", "Caches", "a Cache"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CARTOGRAPHER(CardInfo):
    names = ["Cartographer", "Cartographers", "a Cartographer"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CROSSROADS(CardInfo):
    names = ["Crossroads", "Crossroads", "a Crossroads"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class DEVELOP(CardInfo):
    names = ["Develop", "Develops", "a Develop"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class DUCHESS(CardInfo):
    names = ["Duchess", "Duchesses", "a Duchess"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class EMBASSY(CardInfo):
    names = ["Embassy", "Embassies", "an Embassy"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class FARMLAND(CardInfo):
    names = ["Farmland", "Farmlands", "a Farmland"]
    types = [Types.VICTORY]
    cost = [6, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class FOOLS_GOLD(CardInfo):
    names = ["Fool's Gold", "Fool's Golds", "a Fool's Gold"]
    types = [Types.TREASURE, Types.REACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class HAGGLER(CardInfo):
    names = ["Haggler", "Hagglers", "a Haggler"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class HIGHWAY(CardInfo):
    names = ["Highway", "Highways", "a Highway"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class ILL_GOTTEN_GAINS(CardInfo):
    names = ["Ill-Gotten Gains", "Ill-Gotten Gains", "an Ill-Gotten Gains"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class INN(CardInfo):
    names = ["Inn", "Inns", "an Inn"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class JACK_OF_ALL_TRADES(CardInfo):
    names = ["Jack of All Trades", "Jacks of All Trades", "a Jack of All Trades"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class MANDARIN(CardInfo):
    names = ["Mandarin", "Mandarins", "a Mandarin"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class NOBLE_BRIGAND(CardInfo):
    names = ["Noble Brigand", "Noble Brigands", "a Noble Brigand"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class NOMAD_CAMP(CardInfo):
    names = ["Nomad Camp", "Nomad Camps", "a Nomad Camp"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class OASIS(CardInfo):
    names = ["Oasis", "Oases", "an Oasis"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class ORACLE(CardInfo):
    names = ["Oracle", "Oracles", "an Oracle"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class MARGRAVE(CardInfo):
    names = ["Margrave", "Margraves", "a Margrave"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SCHEME(CardInfo):
    names = ["Scheme", "Schemes", "a Scheme"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SILK_ROAD(CardInfo):
    names = ["Silk Road", "Silk Roads", "a Silk Road"]
    types = [Types.VICTORY]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SPICE_MERCHANT(CardInfo):
    names = ["Spice Merchant", "Spice Merchants", "a Spice Merchant"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class STABLES(CardInfo):
    names = ["Stables", "Stables", "a Stables"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TRADER(CardInfo):
    names = ["Trader", "Traders", "a Trader"]
    types = [Types.ACTION, Types.REACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TUNNEL(CardInfo):
    names = ["Tunnel", "Tunnels", "a Tunnel"]
    types = [Types.VICTORY, Types.REACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state
