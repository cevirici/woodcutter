# -*- coding: utf-8 -*-
from .Utils import *


class Card:
    def __init__(self, cardName, initialZone=None, pileCards=None, orderedPile=True):
        self.cardName = cardName
        self.initialZone = initialZone if initialZone else NeutralZones.SUPPLY
        self.keyCard = pileCards[0] if pileCards else cardName
        self.pileCards = pileCards if pileCards else [cardName]
        self.orderedPile = orderedPile
