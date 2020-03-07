from .Cards import *


class Pile:
    def __init__(self, keyCard, cards, fixedOrder=True):
        self.keyCard = keyCard
        self.acceptedCards = Cards[keyCard].pileCards
        self.cards = cards
        # For non-supply piles, determinedOrder is 'knowable' order - based off
        # reveals, topdecking etc.
        # For supply piles, retroactive knowledge works too.
        if fixedOrder:
            self.determinedOrder = self.cards
        else:
            self.determinedOrder = []

    def shuffle(self):
        if len(set(self.cards)) > 1:
            self.determinedOrder = []

    def addCard(self, card):
        self.cards.append(card)
        self.determinedOrder.insert(0, card)

    def count(self):
        return len(self.cards)

    def contains(self, card):
        if card in self.cards:
            if len(determinedOrder) > 0:
                return determinedOrder[0] == card
            else:
                return True
        return False

    def remove(self, card):
        if not self.contains(card):
            raise InvalidMove

        if len(determinedOrder) > 0:
            determinedOrder.pop(0)
        self.cards.remove(card)
