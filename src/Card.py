# -*- coding: utf-8 -*-
from .Enums import *


class Card:
    def __init__(self, cardInfo, index, startingLocation, player):
        self.name = cardInfo.names[0]
        self.info = cardInfo
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

    def move(self, dest, state):
        if self.location != dest:
            if self.master:
                self.master.slaves.remove(self)
                self.master = None
            if self.slaves:
                for slave in self.slaves:
                    slave.master = None
                self.slaves = []

        if self.location == PlayerZones.PLAY:
            if hasattr(self.info, "onLeavePlay"):
                self.info.onLeavePlay(state, self.index)
        elif dest == PlayerZones.PLAY:
            if hasattr(self.info, "onEnterPlay"):
                self.info.onEnterPlay(state, self.index)
        self.location = dest
