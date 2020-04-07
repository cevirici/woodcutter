# -*- coding: utf-8 -*-
from woodcutter.src.Card import *
from copy import deepcopy


class CardInfo:
    names = ["Back", "Backs", "a Back"]
    types = []
    cost = [0, 0, 0]
    isOrderedPile = False
    initialZone = NeutralZones.SUPPLY
    gainDestination = PlayerZones.DISCARD

    def hasType(self, cardType):
        return cardType in self.types

    def getKeyCard(self):
        if hasattr(self, "keyCard"):
            return self.keyCard
        else:
            return self.names[0]

    def getPileCards(self):
        if hasattr(self, "pileCard"):
            return self.pileCards
        else:
            return [self.names[0]]

    def onBuy(self, state, log):
        state = deepcopy(state)
        coinCost = self.cost[0]
        for (card, amount) in state.reductions:
            if card is None or card == self.names[0]:
                coinCost -= amount
        state.coins -= max(0, coinCost)
        state.potions -= self.cost[1]
        state.buys -= 1
        if self.cost[2] > 0:
            state.stack.append(takeDebt())
        if state.coins >= 0 and state.potions >= 0 and state.buys >= 0:
            state.candidates = state.stack.pop()
            return state
