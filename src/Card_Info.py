from .Enums import *
from .Card import *
from copy import deepcopy


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
        state.candidates = [state.resolutionStack.pop()]
        state.coins += 1
        return state


class SILVER(CardInfo):
    names = ["Silver", "Silvers", "a Silver"]
    types = [Types.TREASURE]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.candidates = [state.resolutionStack.pop()]
        state.coins += 1
        return state


def getCardInfo(card):
    correspondences = {
        "Curse": CURSE,
        "Copper": COPPER,
        "Silver": SILVER,
    }
    if card in correspondences:
        return correspondences[card]()
    else:
        return CardInfo()
