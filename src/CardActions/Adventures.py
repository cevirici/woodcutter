# -*- coding: utf-8 -*-
from .CardInfo import CardInfo
from woodcutter.src.Card import *
from woodcutter.src.Action import Action


class ALMS(CardInfo):
    names = ["Alms", "Alms", "an Alms"]
    types = [Types.EVENT]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class AMULET(CardInfo):
    names = ["Amulet", "Amulets", "an Amulet"]
    types = [Types.ACTION, Types.DURATION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class ARTIFICER(CardInfo):
    names = ["Artificer", "Artificers", "an Artificer"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class BALL(CardInfo):
    names = ["Ball", "Balls", "a Ball"]
    types = [Types.EVENT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class BONFIRE(CardInfo):
    names = ["Bonfire", "Bonfires", "a Bonfire"]
    types = [Types.EVENT]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class BORROW(CardInfo):
    names = ["Borrow", "Borrows", "a Borrow"]
    types = [Types.EVENT]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class BRIDGE_TROLL(CardInfo):
    names = ["Bridge Troll", "Bridge Trolls", "a Bridge Troll"]
    types = [Types.ACTION, Types.DURATION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CARAVAN_GUARD(CardInfo):
    names = ["Caravan Guard", "Caravan Guards", "a Caravan Guard"]
    types = [Types.ACTION, Types.DURATION, Types.REACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CHAMPION(CardInfo):
    names = ["Champion", "Champions", "a Champion"]
    types = [Types.ACTION, Types.DURATION]
    cost = [6, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class COIN_OF_THE_REALM(CardInfo):
    names = ["Coin of the Realm", "Coins of the Realm", "a Coin of the Realm"]
    types = [Types.TREASURE, Types.RESERVE]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class DISCIPLE(CardInfo):
    names = ["Disciple", "Disciples", "a Disciple"]
    types = [Types.ACTION, Types.TRAVELLER]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class DISTANT_LANDS(CardInfo):
    names = ["Distant Lands", "Distant Lands", "a Distant Lands"]
    types = [Types.ACTION, Types.RESERVE, Types.VICTORY]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class DUNGEON(CardInfo):
    names = ["Dungeon", "Dungeons", "a Dungeon"]
    types = [Types.ACTION, Types.DURATION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class DUPLICATE(CardInfo):
    names = ["Duplicate", "Duplicates", "a Duplicate"]
    types = [Types.ACTION, Types.RESERVE]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class EXPEDITION(CardInfo):
    names = ["Expedition", "Expeditions", "an Expedition"]
    types = [Types.EVENT]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class FERRY(CardInfo):
    names = ["Ferry", "Ferries", "a Ferry"]
    types = [Types.EVENT]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class FUGITIVE(CardInfo):
    names = ["Fugitive", "Fugitives", "a Fugitive"]
    types = [Types.ACTION, Types.TRAVELLER]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class GEAR(CardInfo):
    names = ["Gear", "Gears", "a Gear"]
    types = [Types.ACTION, Types.DURATION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class GIANT(CardInfo):
    names = ["Giant", "Giants", "a Giant"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class GUIDE(CardInfo):
    names = ["Guide", "Guides", "a Guide"]
    types = [Types.ACTION, Types.RESERVE]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class HAUNTED_WOODS(CardInfo):
    names = ["Haunted Woods", "Haunted Woods", "a Haunted Woods"]
    types = [Types.ACTION, Types.DURATION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class HERO(CardInfo):
    names = ["Hero", "Heroes", "a Hero"]
    types = [Types.ACTION, Types.TRAVELLER]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class HIRELING(CardInfo):
    names = ["Hireling", "Hirelings", "a Hireling"]
    types = [Types.ACTION, Types.DURATION]
    cost = [6, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class INHERITANCE(CardInfo):
    names = ["Inheritance", "Inheritances", "an Inheritance"]
    types = [Types.EVENT]
    cost = [7, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class LOST_ARTS(CardInfo):
    names = ["Lost Arts", "Lost Arts", "a Lost Arts"]
    types = [Types.EVENT]
    cost = [6, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class LOST_CITY(CardInfo):
    names = ["Lost City", "Lost Cities", "a Lost City"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class MAGPIE(CardInfo):
    names = ["Magpie", "Magpies", "a Magpie"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class MESSENGER(CardInfo):
    names = ["Messenger", "Messengers", "a Messenger"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class MISER(CardInfo):
    names = ["Miser", "Misers", "a Miser"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class MISSION(CardInfo):
    names = ["Mission", "Missions", "a Mission"]
    types = [Types.EVENT]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class PATHFINDING(CardInfo):
    names = ["Pathfinding", "Pathfindings", "a Pathfinding"]
    types = [Types.EVENT]
    cost = [8, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class PAGE(CardInfo):
    names = ["Page", "Pages", "a Page"]
    types = [Types.ACTION, Types.TRAVELLER]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class PEASANT(CardInfo):
    names = ["Peasant", "Peasants", "a Peasant"]
    types = [Types.ACTION, Types.TRAVELLER]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class PILGRIMAGE(CardInfo):
    names = ["Pilgrimage", "Pilgrimages", "a Pilgrimage"]
    types = [Types.EVENT]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class PLAN(CardInfo):
    names = ["Plan", "Plans", "a Plan"]
    types = [Types.EVENT]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class PORT(CardInfo):
    names = ["Port", "Ports", "a Port"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class QUEST(CardInfo):
    names = ["Quest", "Quests", "a Quest"]
    types = [Types.EVENT]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class RANGER(CardInfo):
    names = ["Ranger", "Rangers", "a Ranger"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class RAID(CardInfo):
    names = ["Raid", "Raids", "a Raid"]
    types = [Types.EVENT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class RATCATCHER(CardInfo):
    names = ["Ratcatcher", "Ratcatchers", "a Ratcatcher"]
    types = [Types.ACTION, Types.RESERVE]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class RAZE(CardInfo):
    names = ["Raze", "Razes", "a Raze"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class RELIC(CardInfo):
    names = ["Relic", "Relics", "a Relic"]
    types = [Types.TREASURE, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class ROYAL_CARRIAGE(CardInfo):
    names = ["Royal Carriage", "Royal Carriages", "a Royal Carriage"]
    types = [Types.ACTION, Types.RESERVE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SAVE(CardInfo):
    names = ["Save", "Saves", "a Save"]
    types = [Types.EVENT]
    cost = [1, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SCOUTING_PARTY(CardInfo):
    names = ["Scouting Party", "Scouting Parties", "a Scouting Party"]
    types = [Types.EVENT]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SEAWAY(CardInfo):
    names = ["Seaway", "Seaways", "a Seaway"]
    types = [Types.EVENT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SOLDIER(CardInfo):
    names = ["Soldier", "Soldiers", "a Soldier"]
    types = [Types.ACTION, Types.ATTACK, Types.TRAVELLER]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class STORYTELLER(CardInfo):
    names = ["Storyteller", "Storytellers", "a Storyteller"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SWAMP_HAG(CardInfo):
    names = ["Swamp Hag", "Swamp Hags", "a Swamp Hag"]
    types = [Types.ACTION, Types.DURATION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TEACHER(CardInfo):
    names = ["Teacher", "Teachers", "a Teacher"]
    types = [Types.ACTION, Types.RESERVE]
    cost = [6, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TRAVELLING_FAIR(CardInfo):
    names = ["Travelling Fair", "Travelling Fairs", "a Travelling Fair"]
    types = [Types.EVENT]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TRADE(CardInfo):
    names = ["Trade", "Trades", "a Trade"]
    types = [Types.EVENT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TRAINING(CardInfo):
    names = ["Training", "Trainings", "a Training"]
    types = [Types.EVENT]
    cost = [6, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TRANSMOGRIFY(CardInfo):
    names = ["Transmogrify", "Transmogrifies", "a Transmogrify"]
    types = [Types.ACTION, Types.RESERVE]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TREASURE_TROVE(CardInfo):
    names = ["Treasure Trove", "Treasure Troves", "a Treasure Trove"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TREASURE_HUNTER(CardInfo):
    names = ["Treasure Hunter", "Treasure Hunters", "a Treasure Hunter"]
    types = [Types.ACTION, Types.TRAVELLER]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WARRIOR(CardInfo):
    names = ["Warrior", "Warriors", "a Warrior"]
    types = [Types.ACTION, Types.ATTACK, Types.TRAVELLER]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WINE_MERCHANT(CardInfo):
    names = ["Wine Merchant", "Wine Merchants", "a Wine Merchant"]
    types = [Types.ACTION, Types.RESERVE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state
