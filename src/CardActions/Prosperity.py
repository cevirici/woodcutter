# -*- coding: utf-8 -*-
from .CardInfo import CardInfo
from woodcutter.src.Card import *
from woodcutter.src.Action import Action


class BANK(CardInfo):
    names = ["Bank", "Banks", "a Bank"]
    types = [Types.TREASURE]
    cost = [7, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class BISHOP(CardInfo):
    names = ["Bishop", "Bishops", "a Bishop"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class COLONY(CardInfo):
    names = ["Colony", "Colonies", "a Colony"]
    types = [Types.VICTORY]
    cost = [11, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CONTRABAND(CardInfo):
    names = ["Contraband", "Contrabands", "a Contraband"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class COUNTING_HOUSE(CardInfo):
    names = ["Counting House", "Counting Houses", "a Counting House"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CITY(CardInfo):
    names = ["City", "Cities", "a City"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class EXPAND(CardInfo):
    names = ["Expand", "Expands", "an Expand"]
    types = [Types.ACTION]
    cost = [7, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class FORGE(CardInfo):
    names = ["Forge", "Forges", "a Forge"]
    types = [Types.ACTION]
    cost = [7, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class GRAND_MARKET(CardInfo):
    names = ["Grand Market", "Grand Markets", "a Grand Market"]
    types = [Types.ACTION]
    cost = [6, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class GOONS(CardInfo):
    names = ["Goons", "Goons", "a Goons"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [6, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class HOARD(CardInfo):
    names = ["Hoard", "Hoards", "a Hoard"]
    types = [Types.TREASURE]
    cost = [6, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class KINGS_COURT(CardInfo):
    names = ["King's Court", "King's Courts", "a King's Court"]
    types = [Types.ACTION]
    cost = [7, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class LOAN(CardInfo):
    names = ["Loan", "Loans", "a Loan"]
    types = [Types.TREASURE]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class MINT(CardInfo):
    names = ["Mint", "Mints", "a Mint"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class MONUMENT(CardInfo):
    names = ["Monument", "Monuments", "a Monument"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class MOUNTEBANK(CardInfo):
    names = ["Mountebank", "Mountebanks", "a Mountebank"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class PEDDLER(CardInfo):
    names = ["Peddler", "Peddlers", "a Peddler"]
    types = [Types.ACTION]
    cost = [8, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class PLATINUM(CardInfo):
    names = ["Platinum", "Platina", "a Platinum"]
    types = [Types.TREASURE]
    cost = [9, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class QUARRY(CardInfo):
    names = ["Quarry", "Quarries", "a Quarry"]
    types = [Types.TREASURE]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class RABBLE(CardInfo):
    names = ["Rabble", "Rabbles", "a Rabble"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class ROYAL_SEAL(CardInfo):
    names = ["Royal Seal", "Royal Seals", "a Royal Seal"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TALISMAN(CardInfo):
    names = ["Talisman", "Talismans", "a Talisman"]
    types = [Types.TREASURE]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TRADE_ROUTE(CardInfo):
    names = ["Trade Route", "Trade Routes", "a Trade Route"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class VAULT(CardInfo):
    names = ["Vault", "Vaults", "a Vault"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class VENTURE(CardInfo):
    names = ["Venture", "Ventures", "a Venture"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WATCHTOWER(CardInfo):
    names = ["Watchtower", "Watchtowers", "a Watchtower"]
    types = [Types.ACTION, Types.REACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WORKERS_VILLAGE(CardInfo):
    names = ["Worker's Village", "Worker's Villages", "a Worker's Village"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state
