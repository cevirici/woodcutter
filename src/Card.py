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
        self.slaves = []

    def __repr__(self):
        return "{}({})".format(self.index, self.name)

    def __hash__(self):
        return self.index

    def move(self, dest):
        if self.location == PlayerZones.PLAY:
            if self.master:
                self.master.slaves.remove(self)
                self.master = None
            if self.slaves:
                for slave in self.slaves:
                    slave.master = None
                self.slaves = []
        self.location = dest
