# -*- coding: utf-8 -*-
from .CardInfo import CardInfo
from woodcutter.src.Card import *
from woodcutter.src.Action import Action


class BLACK_CAT(CardInfo):
    names = ["Black Cat", "Black Cats", "a Black Cat"]
    types = [Types.ACTION, Types.ATTACK, Types.REACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SLEIGH(CardInfo):
    names = ["Sleigh", "Sleighs", "a Sleigh"]
    types = [Types.ACTION, Types.REACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SUPPLIES(CardInfo):
    names = ["Supplies", "Supplies", "a Supplies"]
    types = [Types.TREASURE]
    cost = [2, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CAMEL_TRAIN(CardInfo):
    names = ["Camel Train", "Camel Trains", "a Camel Train"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class GOATHERD(CardInfo):
    names = ["Goatherd", "Goatherds", "a Goatherd"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SCRAP(CardInfo):
    names = ["Scrap", "Scraps", "a Scrap"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SHEEPDOG(CardInfo):
    names = ["Sheepdog", "Sheepdogs", "a Sheepdog"]
    types = [Types.ACTION, Types.REACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SNOWY_VILLAGE(CardInfo):
    names = ["Snowy Village", "Snowy Villages", "a Snowy Village"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class STOCKPILE(CardInfo):
    names = ["Stockpile", "Stockpiles", "a Stockpile"]
    types = [Types.TREASURE]
    cost = [3, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class BOUNTY_HUNTER(CardInfo):
    names = ["Bounty Hunter", "Bounty Hunters", "a Bounty Hunter"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CARDINAL(CardInfo):
    names = ["Cardinal", "Cardinals", "a Cardinal"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [4, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CAVALRY(CardInfo):
    names = ["Cavalry", "Cavalries", "a Cavalry"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class GROOM(CardInfo):
    names = ["Groom", "Grooms", "a Groom"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class HOSTELRY(CardInfo):
    names = ["Hostelry", "Hostelries", "a Hostelry"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class VILLAGE_GREEN(CardInfo):
    names = ["Village Green", "Village Greens", "a Village Green"]
    types = [Types.ACTION, Types.DURATION, Types.REACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class BARGE(CardInfo):
    names = ["Barge", "Barges", "a Barge"]
    types = [Types.ACTION, Types.DURATION]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class COVEN(CardInfo):
    names = ["Coven", "Covens", "a Coven"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class DISPLACE(CardInfo):
    names = ["Displace", "Displaces", "a Displace"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class FALCONER(CardInfo):
    names = ["Falconer", "Falconers", "a Falconer"]
    types = [Types.ACTION, Types.REACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class FISHERMAN(CardInfo):
    names = ["Fisherman", "Fishermen", "a Fisherman"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class GATEKEEPER(CardInfo):
    names = ["Gatekeeper", "Gatekeepers", "a Gatekeeper"]
    types = [Types.ACTION, Types.DURATION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class HUNTING_LODGE(CardInfo):
    names = ["Hunting Lodge", "Hunting Lodges", "a Hunting Lodge"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class KILN(CardInfo):
    names = ["Kiln", "Kilns", "a Kiln"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class LIVERY(CardInfo):
    names = ["Livery", "Liveries", "a Livery"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class MASTERMIND(CardInfo):
    names = ["Mastermind", "Masterminds", "a Mastermind"]
    types = [Types.ACTION, Types.DURATION]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class PADDOCK(CardInfo):
    names = ["Paddock", "Paddocks", "a Paddock"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SANCTUARY(CardInfo):
    names = ["Sanctuary", "Sanctuaries", "a Sanctuary"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class DESTRIER(CardInfo):
    names = ["Destrier", "Destriers", "a Destrier"]
    types = [Types.ACTION]
    cost = [6, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WAYFARER(CardInfo):
    names = ["Wayfarer", "Wayfarers", "a Wayfarer"]
    types = [Types.ACTION]
    cost = [6, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class ANIMAL_FAIR(CardInfo):
    names = ["Animal Fair", "Animal Fairs", "an Animal Fair"]
    types = [Types.ACTION]
    cost = [7, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class HORSE(CardInfo):
    names = ["Horse", "Horses", "a Horse"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WAY_OF_THE_BUTTERFLY(CardInfo):
    names = ["Way of the Butterfly", "Way of the Butterfly", "Way of the Butterfly"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WAY_OF_THE_CAMEL(CardInfo):
    names = ["Way of the Camel", "Way of the Camel", "Way of the Camel"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WAY_OF_THE_CHAMELEON(CardInfo):
    names = ["Way of the Chameleon", "Way of the Chameleon", "Way of the Chameleon"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WAY_OF_THE_FROG(CardInfo):
    names = ["Way of the Frog", "Way of the Frog", "Way of the Frog"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WAY_OF_THE_GOAT(CardInfo):
    names = ["Way of the Goat", "Way of the Goat", "Way of the Goat"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WAY_OF_THE_HORSE(CardInfo):
    names = ["Way of the Horse", "Way of the Horse", "Way of the Horse"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WAY_OF_THE_MOLE(CardInfo):
    names = ["Way of the Mole", "Way of the Mole", "Way of the Mole"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WAY_OF_THE_MONKEY(CardInfo):
    names = ["Way of the Monkey", "Way of the Monkey", "Way of the Monkey"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WAY_OF_THE_MOUSE(CardInfo):
    names = ["Way of the Mouse", "Way of the Mouse", "Way of the Mouse"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WAY_OF_THE_MULE(CardInfo):
    names = ["Way of the Mule", "Way of the Mule", "Way of the Mule"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WAY_OF_THE_OTTER(CardInfo):
    names = ["Way of the Otter", "Way of the Otter", "Way of the Otter"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WAY_OF_THE_OWL(CardInfo):
    names = ["Way of the Owl", "Way of the Owl", "Way of the Owl"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WAY_OF_THE_OX(CardInfo):
    names = ["Way of the Ox", "Way of the Ox", "Way of the Ox"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WAY_OF_THE_PIG(CardInfo):
    names = ["Way of the Pig", "Way of the Pig", "Way of the Pig"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WAY_OF_THE_RAT(CardInfo):
    names = ["Way of the Rat", "Way of the Rat", "Way of the Rat"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WAY_OF_THE_SEAL(CardInfo):
    names = ["Way of the Seal", "Way of the Seal", "Way of the Seal"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WAY_OF_THE_SHEEP(CardInfo):
    names = ["Way of the Sheep", "Way of the Sheep", "Way of the Sheep"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WAY_OF_THE_SQUIRREL(CardInfo):
    names = ["Way of the Squirrel", "Way of the Squirrel", "Way of the Squirrel"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WAY_OF_THE_TURTLE(CardInfo):
    names = ["Way of the Turtle", "Way of the Turtle", "Way of the Turtle"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WAY_OF_THE_WORM(CardInfo):
    names = ["Way of the Worm", "Way of the Worm", "Way of the Worm"]
    types = [Types.WAY]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class DELAY(CardInfo):
    names = ["Delay", "Delay", "Delay"]
    types = [Types.EVENT]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class DESPERATION(CardInfo):
    names = ["Desperation", "Desperation", "Desperation"]
    types = [Types.EVENT]
    cost = [0, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class GAMBLE(CardInfo):
    names = ["Gamble", "Gamble", "Gamble"]
    types = [Types.EVENT]
    cost = [2, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class PURSUE(CardInfo):
    names = ["Pursue", "Pursue", "Pursue"]
    types = [Types.EVENT]
    cost = [2, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class RIDE(CardInfo):
    names = ["Ride", "Ride", "Ride"]
    types = [Types.EVENT]
    cost = [2, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TOIL(CardInfo):
    names = ["Toil", "Toil", "Toil"]
    types = [Types.EVENT]
    cost = [2, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class ENHANCE(CardInfo):
    names = ["Enhance", "Enhance", "Enhance"]
    types = [Types.EVENT]
    cost = [3, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class MARCH(CardInfo):
    names = ["March", "March", "March"]
    types = [Types.EVENT]
    cost = [3, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TRANSPORT(CardInfo):
    names = ["Transport", "Transport", "Transport"]
    types = [Types.EVENT]
    cost = [3, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class BANISH(CardInfo):
    names = ["Banish", "Banish", "Banish"]
    types = [Types.EVENT]
    cost = [4, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class BARGAIN(CardInfo):
    names = ["Bargain", "Bargain", "Bargain"]
    types = [Types.EVENT]
    cost = [4, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class INVEST(CardInfo):
    names = ["Invest", "Invest", "Invest"]
    types = [Types.EVENT]
    cost = [4, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SEIZE_THE_DAY(CardInfo):
    names = ["Seize The Day", "Seize The Day", "Seize The Day"]
    types = [Types.EVENT]
    cost = [4, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class COMMERCE(CardInfo):
    names = ["Commerce", "Commerce", "Commerce"]
    types = [Types.EVENT]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class DEMAND(CardInfo):
    names = ["Demand", "Demand", "Demand"]
    types = [Types.EVENT]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class STAMPEDE(CardInfo):
    names = ["Stampede", "Stampede", "Stampede"]
    types = [Types.EVENT]
    cost = [5, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class REAP(CardInfo):
    names = ["Reap", "Reap", "Reap"]
    types = [Types.EVENT]
    cost = [7, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class ENCLAVE(CardInfo):
    names = ["Enclave", "Enclave", "Enclave"]
    types = [Types.EVENT]
    cost = [8, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class ALLIANCE(CardInfo):
    names = ["Alliance", "Alliance", "Alliance"]
    types = [Types.EVENT]
    cost = [10, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class POPULATE(CardInfo):
    names = ["Populate", "Populate", "Populate"]
    types = [Types.EVENT]
    cost = [10, 0, 0]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state
