# -*- coding: utf-8 -*-
from .Enums import *


class Card:
    def __init__(self, name, index, startingLocation, player):
        self.name = name
        self.index = index
        self.location = startingLocation
        self.player = player
        self.stayingOut = 0
        self.master = None
        self.slave = None

    def __repr__(self):
        return "{}({})".format(self.index, self.name)

    def __hash__(self):
        return self.index

    def move(self, dest):
        if self.location == PlayerZones.PLAY:
            self.master, self.slave = (None, None)
        self.location = dest
