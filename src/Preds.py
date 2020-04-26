# -*- coding: utf-8 -*-
from .Enums import *


def getArgTypes(predName):
    correspondences = {
        "PLAYER_GETS_VP_FROM": [argTypes.NUMBER, argTypes.CARD],
        "PLUS_ACTION_FROM": [argTypes.NUMBER, argTypes.CARD],
        "PLUS_BUY_FROM": [argTypes.NUMBER, argTypes.CARD],
        "DRAWS_FROM": [argTypes.CARD],
        "PLUS_COIN_FROM": [argTypes.NUMBER, argTypes.CARD],
        "GETS_COFFERS_FROM": [argTypes.NUMBER, argTypes.CARD],
        "GETS_VILLAGERS_FROM": [argTypes.NUMBER, argTypes.CARD],
        "GETS_COFFER_FROM": [argTypes.NUMBER, argTypes.CARD],
        "GETS_VILLAGER_FROM": [argTypes.NUMBER, argTypes.CARD],
        "GETS_ACTIONS_FROM": [argTypes.NUMBER, argTypes.CARD],
        "GETS_BUYS_FROM": [argTypes.NUMBER, argTypes.CARD],
        "GETS_COINS_FROM": [argTypes.NUMBER, argTypes.CARD],
        "GETS_ACTION_FROM": [argTypes.NUMBER, argTypes.CARD],
        "GETS_BUY_FROM": [argTypes.NUMBER, argTypes.CARD],
        "GETS_COIN_FROM": [argTypes.NUMBER, argTypes.CARD],
    }
    if predName in correspondences:
        return correspondences[predName]
    else:
        return None
