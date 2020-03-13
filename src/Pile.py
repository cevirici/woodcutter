from .GenericActions import *


class Pile:
    def __init__(self, keyCard, cards):
        self.keyCard = keyCard
        self.acceptedCards = getCardInfo(keyCard).getPileCards()
        self.cards = cards

    def __repr__(self):
        return repr(self.cards)

    def shuffle(self):
        if len(set(self.cards)) > 1:
            self.determinedOrder = []

    def addCard(self, card):
        self.cards.insert(0, card)

    def count(self):
        return len(self.cards)

    def contains(self, cardName):
        for card in self.cards:
            if card.name == cardName:
                return True
        return False

    def remove(self, cardName):
        for card in self.cards:
            if card.name == cardName:
                self.cards.remove(card)
                return card
        return False

    def removeAll(self):
        self.cards = []
