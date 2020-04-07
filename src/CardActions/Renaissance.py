# -*- coding: utf-8 -*-
from .CardInfo import CardInfo
from woodcutter.src.Card import *
from woodcutter.src.Action import Action


class ACTING_TROUPE(CardInfo):
    names = ["Acting Troupe", "Acting Troupes", "an Acting Troupe"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class BORDER_GUARD(CardInfo):
    names = ["Border Guard", "Border Guards", "a Border Guard"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CARGO_SHIP(CardInfo):
    names = ["Cargo Ship", "Cargo Ships", "a Cargo Ship"]
    types = [Types.ACTION, Types.DURATION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class DUCAT(CardInfo):
    names = ["Ducat", "Ducats", "a Ducat"]
    types = [Types.TREASURE]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class EXPERIMENT(CardInfo):
    names = ["Experiment", "Experiments", "an Experiment"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class FLAG_BEARER(CardInfo):
    names = ["Flag Bearer", "Flag Bearers", "a Flag Bearer"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class HIDEOUT(CardInfo):
    names = ["Hideout", "Hideouts", "a Hideout"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class INVENTOR(CardInfo):
    names = ["Inventor", "Inventors", "an Inventor"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class IMPROVE(CardInfo):
    names = ["Improve", "Improves", "an Improve"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class LACKEYS(CardInfo):
    names = ["Lackeys", "Lackeys", "a Lackeys"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class MOUNTAIN_VILLAGE(CardInfo):
    names = ["Mountain Village", "Mountain Villages", "a Mountain Village"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class PATRON(CardInfo):
    names = ["Patron", "Patrons", "a Patron"]
    types = [Types.ACTION, Types.REACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class PRIEST(CardInfo):
    names = ["Priest", "Priests", "a Priest"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class RESEARCH(CardInfo):
    names = ["Research", "Researches", "a Research"]
    types = [Types.ACTION, Types.DURATION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SILK_MERCHANT(CardInfo):
    names = ["Silk Merchant", "Silk Merchants", "a Silk Merchant"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class OLD_WITCH(CardInfo):
    names = ["Old Witch", "Old Witches", "an Old Witch"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class RECRUITER(CardInfo):
    names = ["Recruiter", "Recruiters", "a Recruiter"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SCEPTER(CardInfo):
    names = ["Scepter", "Scepters", "a Scepter"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SCHOLAR(CardInfo):
    names = ["Scholar", "Scholars", "a Scholar"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SCULPTOR(CardInfo):
    names = ["Sculptor", "Sculptors", "a Sculptor"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SEER(CardInfo):
    names = ["Seer", "Seers", "a Seer"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SPICES(CardInfo):
    names = ["Spices", "Spices", "a Spices"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SWASHBUCKLER(CardInfo):
    names = ["Swashbuckler", "Swashbucklers", "a Swashbuckler"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TREASURER(CardInfo):
    names = ["Treasurer", "Treasurers", "a Treasurer"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class VILLAIN(CardInfo):
    names = ["Villain", "Villains", "a Villain"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class FLAG(CardInfo):
    names = ["Flag", "Flags", "the Flag"]
    types = [Types.ARTIFACT]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class HORN(CardInfo):
    names = ["Horn", "Horns", "the Horn"]
    types = [Types.ARTIFACT]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class KEY(CardInfo):
    names = ["Key", "Keys", "the Key"]
    types = [Types.ARTIFACT]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class LANTERN(CardInfo):
    names = ["Lantern", "Lanterns", "the Lantern"]
    types = [Types.ARTIFACT]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TREASURE_CHEST(CardInfo):
    names = ["Treasure Chest", "Treasure Chests", "the Treasure Chest"]
    types = [Types.ARTIFACT]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class ACADEMY(CardInfo):
    names = ["Academy", "Academy", "Academy"]
    types = [Types.PROJECT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class BARRACKS(CardInfo):
    names = ["Barracks", "Barracks", "Barracks"]
    types = [Types.PROJECT]
    cost = [6, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CANAL(CardInfo):
    names = ["Canal", "Canal", "Canal"]
    types = [Types.PROJECT]
    cost = [7, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CAPITALISM(CardInfo):
    names = ["Capitalism", "Capitalism", "Capitalism"]
    types = [Types.PROJECT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CATHEDRAL(CardInfo):
    names = ["Cathedral", "Cathedral", "Cathedral"]
    types = [Types.PROJECT]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CITADEL(CardInfo):
    names = ["Citadel", "Citadel", "Citadel"]
    types = [Types.PROJECT]
    cost = [8, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CITY_GATE(CardInfo):
    names = ["City Gate", "City Gate", "City Gate"]
    types = [Types.PROJECT]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CROP_ROTATION(CardInfo):
    names = ["Crop Rotation", "Crop Rotation", "Crop Rotation"]
    types = [Types.PROJECT]
    cost = [6, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class EXPLORATION(CardInfo):
    names = ["Exploration", "Exploration", "Exploration"]
    types = [Types.PROJECT]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class FAIR(CardInfo):
    names = ["Fair", "Fair", "Fair"]
    types = [Types.PROJECT]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class FLEET(CardInfo):
    names = ["Fleet", "Fleet", "Fleet"]
    types = [Types.PROJECT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class GUILDHALL(CardInfo):
    names = ["Guildhall", "Guildhall", "Guildhall"]
    types = [Types.PROJECT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class INNOVATION(CardInfo):
    names = ["Innovation", "Innovation", "Innovation"]
    types = [Types.PROJECT]
    cost = [6, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class PAGEANT(CardInfo):
    names = ["Pageant", "Pageant", "Pageant"]
    types = [Types.PROJECT]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class PIAZZA(CardInfo):
    names = ["Piazza", "Piazza", "Piazza"]
    types = [Types.PROJECT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class ROAD_NETWORK(CardInfo):
    names = ["Road Network", "Road Network", "Road Network"]
    types = [Types.PROJECT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SEWERS(CardInfo):
    names = ["Sewers", "Sewers", "Sewers"]
    types = [Types.PROJECT]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SILOS(CardInfo):
    names = ["Silos", "Silos", "Silos"]
    types = [Types.PROJECT]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SINISTER_PLOT(CardInfo):
    names = ["Sinister Plot", "Sinister Plot", "Sinister Plot"]
    types = [Types.PROJECT]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class STAR_CHART(CardInfo):
    names = ["Star Chart", "Star Chart", "Star Chart"]
    types = [Types.PROJECT]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state
