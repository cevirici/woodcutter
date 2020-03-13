# -*- coding: utf-8 -*-
from .Enums import *
from .Card import *
from copy import deepcopy
from .GenericActions import *


class CardInfo:
    names = ["Back", "Backs", "a Back"]
    types = []

    def hasType(self, cardType):
        return cardType in self.types


class CURSE(CardInfo):
    names = ["Curse", "Curses", "a Curse"]
    types = [Types.CURSE]


class COPPER(CardInfo):
    names = ["Copper", "Coppers", "a Copper"]
    types = [Types.TREASURE]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.candidates = [state.stack.pop()]
        state.coins += 1
        return state


class SILVER(CardInfo):
    names = ["Silver", "Silvers", "a Silver"]
    types = [Types.TREASURE]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.candidates = [state.stack.pop()]
        state.coins += 2
        return state


class GOLD(CardInfo):
    names = ["Gold", "Golds", "a Gold"]
    types = [Types.TREASURE]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.candidates = [state.stack.pop()]
        state.coins += 3
        return state


class ESTATE(CardInfo):
    names = ["Estate", "Estates", "an Estate"]
    types = [Types.VICTORY]


class DUCHY(CardInfo):
    names = ["Duchy", "Duchies", "a Duchy"]
    types = [Types.VICTORY]


class PROVINCE(CardInfo):
    names = ["Province", "Provinces", "a Province"]
    types = [Types.VICTORY]


class ARTISAN(CardInfo):
    names = ["Artisan", "Artisans", "an Artisan"]
    types = [Types.ACTION]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [
            gain(NeutralZones.SUPPLY, PlayerZones.HAND),
            topdeck(PlayerZones.HAND, PlayerZones.DECK),
        ]
        state.candidates = [state.stack.pop()]
        return state


class BANDIT(CardInfo):
    names = ["Bandit", "Bandits", "a Bandit"]
    types = [Types.ACTION, Types.ATTACK]

    # def onPlay(self, state, log):
    #     state = deepcopy(state)
    #     state.stack += [state.stack.pop()]
    #     state.coins += 3
    #     return state


class MILITIA(CardInfo):
    names = ["Militia", "Militias", "a Militia"]
    types = [Types.ACTION, Types.ATTACK]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [discard(PlayerZones.HAND, PlayerZones.DISCARD), getCoin()]
        state.candidates = [state.stack.pop()]
        return state


class WITCH(CardInfo):
    names = ["Witch", "Witches", "a Witch"]
    types = [Types.ACTION, Types.ATTACK]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [gain(NeutralZones.SUPPLY, PlayerZones.DISCARD), drawN(2)]
        state.candidates = [state.stack.pop()]
        return state


def getCardInfo(card):
    correspondences = {
        "Curse": CURSE,
        "Copper": COPPER,
        "Silver": SILVER,
        "Gold": GOLD,
        "Estate": ESTATE,
        "Duchy": DUCHY,
        "Province": PROVINCE,
        "Artisan": ARTISAN,
        "Bandit": BANDIT,
        "Militia": MILITIA,
        "Witch": WITCH,
    }
    if card in correspondences:
        return correspondences[card]()
    else:
        return CardInfo()
