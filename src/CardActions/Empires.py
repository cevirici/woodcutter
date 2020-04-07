# -*- coding: utf-8 -*-
from .CardInfo import CardInfo
from woodcutter.src.Card import *
from woodcutter.src.Action import Action


class ENCAMPMENT(CardInfo):
    names = ["Encampment", "Encampments", "an Encampment"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class PLUNDER(CardInfo):
    names = ["Plunder", "Plunders", "a Plunder"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class PATRICIAN(CardInfo):
    names = ["Patrician", "Patricians", "a Patrician"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class EMPORIUM(CardInfo):
    names = ["Emporium", "Emporia", "an Emporium"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SETTLERS(CardInfo):
    names = ["Settlers", "Settlers", "a Settlers"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class BUSTLING_VILLAGE(CardInfo):
    names = ["Bustling Village", "Bustling Villages", "a Bustling Village"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CATAPULT(CardInfo):
    names = ["Catapult", "Catapults", "a Catapult"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class ROCKS(CardInfo):
    names = ["Rocks", "Rocks", "a Rocks"]
    types = [Types.TREASURE]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class GLADIATOR(CardInfo):
    names = ["Gladiator", "Gladiators", "a Gladiator"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class FORTUNE(CardInfo):
    names = ["Fortune", "Fortunes", "a Fortune"]
    types = [Types.TREASURE]
    cost = [8, 0, 8]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CASTLES(CardInfo):
    names = ["Castles", "Castles", "a Castles"]
    types = [Types.VICTORY, Types.CASTLE]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class HUMBLE_CASTLE(CardInfo):
    names = ["Humble Castle", "Humble Castles", "a Humble Castle"]
    types = [Types.TREASURE, Types.VICTORY, Types.CASTLE]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CRUMBLING_CASTLE(CardInfo):
    names = ["Crumbling Castle", "Crumbling Castles", "a Crumbling Castle"]
    types = [Types.VICTORY, Types.CASTLE]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SMALL_CASTLE(CardInfo):
    names = ["Small Castle", "Small Castles", "a Small Castle"]
    types = [Types.ACTION, Types.VICTORY, Types.CASTLE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class HAUNTED_CASTLE(CardInfo):
    names = ["Haunted Castle", "Haunted Castles", "a Haunted Castle"]
    types = [Types.VICTORY, Types.CASTLE]
    cost = [6, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class OPULENT_CASTLE(CardInfo):
    names = ["Opulent Castle", "Opulent Castles", "an Opulent Castle"]
    types = [Types.ACTION, Types.VICTORY, Types.CASTLE]
    cost = [7, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SPRAWLING_CASTLE(CardInfo):
    names = ["Sprawling Castle", "Sprawling Castles", "a Sprawling Castle"]
    types = [Types.VICTORY, Types.CASTLE]
    cost = [8, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class GRAND_CASTLE(CardInfo):
    names = ["Grand Castle", "Grand Castles", "a Grand Castle"]
    types = [Types.VICTORY, Types.CASTLE]
    cost = [9, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class KINGS_CASTLE(CardInfo):
    names = ["King's Castle", "King's Castles", "a King's Castle"]
    types = [Types.VICTORY, Types.CASTLE]
    cost = [10, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class ADVANCE(CardInfo):
    names = ["Advance", "Advances", "an Advance"]
    types = [Types.EVENT]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class ANNEX(CardInfo):
    names = ["Annex", "Annexes", "an Annex"]
    types = [Types.EVENT]
    cost = [0, 0, 8]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class ARCHIVE(CardInfo):
    names = ["Archive", "Archives", "an Archive"]
    types = [Types.ACTION, Types.DURATION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class AQUEDUCT(CardInfo):
    names = ["Aqueduct", "Aqueducts", "an Aqueduct"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class ARENA(CardInfo):
    names = ["Arena", "Arenas", "an Arena"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class BANDIT_FORT(CardInfo):
    names = ["Bandit Fort", "Bandit Forts", "a Bandit Fort"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class BANQUET(CardInfo):
    names = ["Banquet", "Banquets", "a Banquet"]
    types = [Types.EVENT]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class BASILICA(CardInfo):
    names = ["Basilica", "Basilicas", "a Basilica"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class BATHS(CardInfo):
    names = ["Baths", "Baths", "a Baths"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class BATTLEFIELD(CardInfo):
    names = ["Battlefield", "Battlefields", "a Battlefield"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CAPITAL(CardInfo):
    names = ["Capital", "Capitals", "a Capital"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CHARM(CardInfo):
    names = ["Charm", "Charms", "a Charm"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CHARIOT_RACE(CardInfo):
    names = ["Chariot Race", "Chariot Races", "a Chariot Race"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CITY_QUARTER(CardInfo):
    names = ["City Quarter", "City Quarters", "a City Quarter"]
    types = [Types.ACTION]
    cost = [0, 0, 8]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class COLONNADE(CardInfo):
    names = ["Colonnade", "Colonnades", "a Colonnade"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CONQUEST(CardInfo):
    names = ["Conquest", "Conquests", "a Conquest"]
    types = [Types.EVENT]
    cost = [6, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CROWN(CardInfo):
    names = ["Crown", "Crowns", "a Crown"]
    types = [Types.ACTION, Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class DELVE(CardInfo):
    names = ["Delve", "Delves", "a Delve"]
    types = [Types.EVENT]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class DEFILED_SHRINE(CardInfo):
    names = ["Defiled Shrine", "Defiled Shrines", "a Defiled Shrine"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class DOMINATE(CardInfo):
    names = ["Dominate", "Dominates", "a Dominate"]
    types = [Types.EVENT]
    cost = [14, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class DONATE(CardInfo):
    names = ["Donate", "Donates", "a Donate"]
    types = [Types.EVENT]
    cost = [0, 0, 8]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class ENCHANTRESS(CardInfo):
    names = ["Enchantress", "Enchantresses", "an Enchantress"]
    types = [Types.ACTION, Types.DURATION, Types.ATTACK]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class ENGINEER(CardInfo):
    names = ["Engineer", "Engineers", "an Engineer"]
    types = [Types.ACTION]
    cost = [0, 0, 4]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class FARMERS_MARKET(CardInfo):
    names = ["Farmers' Market", "Farmers' Markets", "a Farmers' Market"]
    types = [Types.ACTION, Types.GATHERING]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class FORUM(CardInfo):
    names = ["Forum", "Forums", "a Forum"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class FOUNTAIN(CardInfo):
    names = ["Fountain", "Fountains", "a Fountain"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class GROUNDSKEEPER(CardInfo):
    names = ["Groundskeeper", "Groundskeepers", "a Groundskeeper"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class KEEP(CardInfo):
    names = ["Keep", "Keeps", "a Keep"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class LABYRINTH(CardInfo):
    names = ["Labyrinth", "Labyrinths", "a Labyrinth"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class LEGIONARY(CardInfo):
    names = ["Legionary", "Legionaries", "a Legionary"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class MOUNTAIN_PASS(CardInfo):
    names = ["Mountain Pass", "Mountain Passes", "a Mountain Pass"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class MUSEUM(CardInfo):
    names = ["Museum", "Museums", "a Museum"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class OBELISK(CardInfo):
    names = ["Obelisk", "Obelisks", "an Obelisk"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class ORCHARD(CardInfo):
    names = ["Orchard", "Orchards", "an Orchard"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class OVERLORD(CardInfo):
    names = ["Overlord", "Overlords", "an Overlord"]
    types = [Types.ACTION, Types.COMMAND]
    cost = [0, 0, 8]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class PALACE(CardInfo):
    names = ["Palace", "Palaces", "a Palace"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class RITUAL(CardInfo):
    names = ["Ritual", "Rituals", "a Ritual"]
    types = [Types.EVENT]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class ROYAL_BLACKSMITH(CardInfo):
    names = ["Royal Blacksmith", "Royal Blacksmiths", "a Royal Blacksmith"]
    types = [Types.ACTION]
    cost = [0, 0, 8]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SACRIFICE(CardInfo):
    names = ["Sacrifice", "Sacrifices", "a Sacrifice"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SALT_THE_EARTH(CardInfo):
    names = ["Salt the Earth", "Salt the Earths", "a Salt the Earth"]
    types = [Types.EVENT]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TAX(CardInfo):
    names = ["Tax", "Taxes", "a Tax"]
    types = [Types.EVENT]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TEMPLE(CardInfo):
    names = ["Temple", "Temples", "a Temple"]
    types = [Types.ACTION, Types.GATHERING]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TOMB(CardInfo):
    names = ["Tomb", "Tombs", "a Tomb"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TOWER(CardInfo):
    names = ["Tower", "Towers", "a Tower"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TRIUMPH(CardInfo):
    names = ["Triumph", "Triumphs", "a Triumph"]
    types = [Types.EVENT]
    cost = [0, 0, 5]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TRIUMPHAL_ARCH(CardInfo):
    names = ["Triumphal Arch", "Triumphal Arches", "a Triumphal Arch"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class VILLA(CardInfo):
    names = ["Villa", "Villas", "a Villa"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WALL(CardInfo):
    names = ["Wall", "Walls", "a Wall"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WOLF_DEN(CardInfo):
    names = ["Wolf Den", "Wolf Dens", "a Wolf Den"]
    types = [Types.LANDMARK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WEDDING(CardInfo):
    names = ["Wedding", "Weddings", "a Wedding"]
    types = [Types.EVENT]
    cost = [4, 0, 3]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WILD_HUNT(CardInfo):
    names = ["Wild Hunt", "Wild Hunts", "a Wild Hunt"]
    types = [Types.ACTION, Types.GATHERING]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WINDFALL(CardInfo):
    names = ["Windfall", "Windfalls", "a Windfall"]
    types = [Types.EVENT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state
