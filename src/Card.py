# -*- coding: utf-8 -*-
class Card:
    def __init__(self, name, index):
        self.name = name
        self.index = index
        self.stayingOut = 0
        self.associations = []

    def __repr__(self):
        return "{}({})".format(self.index, self.name)
