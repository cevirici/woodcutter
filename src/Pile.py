from .GenericActions import *
from copy import copy


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

    def contains(self, card):
        return card in self.cards

    def remove(self, card):
        if not self.contains(card):
            return False

        self.cards.remove(card)

    def removeAll(self):
        self.cards = []
