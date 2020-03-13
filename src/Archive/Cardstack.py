# -*- coding: utf-8 -*-
from copy import deepcopy
from .Standards import *


class Cardstack:
    def __init__(self, cards):
        self.cards = {}
        for c in cards:
            self.cards[c] = cards[c]

    def __iter__(self):
        for card in list(self.cards):
            yield str(card)

    def __delitem__(self, item):
        if item in self:
            del self.cards[item]

    def __getitem__(self, item):
        return self.cards[item] if item in self.cards else 0

    def __setitem__(self, item, value):
        if value > 0:
            self.cards[item] = value
        else:
            del self[item]

    def __add__(self, other):
        t = deepcopy(self)
        for c in other:
            if c != "NOTHING":
                t[c] += other[c]
        return t

    def __sub__(self, other):
        t = deepcopy(self)
        for c in other:
            if c != "NOTHING":
                t[c] -= other[c]
        return t

    def __gt__(self, other):
        for card in other:
            if other[card] > self[card]:
                return False
        return True

    def __str__(self):
        return "<br>".join(["{}:{}".format(self.cards[i], str(i)) for i in self.cards])

    def __repr__(self):
        sortedCards = sorted(self.cards, key=lambda c: cardOrder[c])
        return "+".join(
            ["{}:{}".format(self.cards[i], repr(Cards[i])) for i in sortedCards]
        )

    def __len__(self):
        return sum([self[item] for item in self if item != "NOTHING"])

    def cardList(self):
        return list(self.cards)

    def getCards(self):
        return self.cards

    def strip(self):
        t = deepcopy(self)
        for c in ["NOTHING", "CARD"]:
            del t[c]

        return t

    @property
    def primary(self):
        if len(self) > 0:
            return list(self.cards.keys())[0]
        else:
            return "CARD"

    def merge(self, other):
        choices = [x for x in [self, other] if "CARD" not in x and "NOTHING" not in x]
        if len(choices) == 2:
            if self.cards != other.cards:
                print([self, other])
            output = deepcopy(self.strip())

            for card in other.strip():
                if card in output:
                    output[card] = min(self[card], other[card])
            return output
        elif len(choices) == 1:
            return choices[0]
        else:
            choices = sorted([self, other], key=lambda x: x["CARD"] + x["NOTHING"])
            return choices[0]
