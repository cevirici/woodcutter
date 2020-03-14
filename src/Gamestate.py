# -*- coding: utf-8 -*-
from .Card import *
from .Pile import *
from .Utils import *


class Gamestate:
    def __init__(self):
        self.cards = []
        self.zones = {z: [[] for p in range(PLAYER_COUNT)] for z in PlayerZones}
        self.zones.update({z: [] for z in NeutralZones})

        self.player = 0
        self.turnNumber = 0
        self.turnType = TurnTypes.PREGAME

        self.stack = []
        self.logLine = 0
        self.candidates = []
        self.selectedMove = None

        self.actions = 0
        self.buys = 0
        self.coins = 0
        self.potions = 0
        self.coffers = [0 for p in range(PLAYER_COUNT)]
        self.debt = [0 for p in range(PLAYER_COUNT)]
        self.villagers = [0 for p in range(PLAYER_COUNT)]

        self.reductions = []
        self.turnStarts = []
        self.cleanupEffects = []

    def __repr__(self):
        return repr(self.move)

    def getZone(self, zoneName, player):
        if player == -1:
            player = self.player
        if isinstance(zoneName, PlayerZones):
            return self.zones[zoneName][player]
        else:
            return self.zones[zoneName]

    def zoneCount(self, zoneName, player=-1):
        return len(self.getZone(zoneName, player))

    def zoneContains(self, cardName, zoneName, player=-1):
        for card in self.getZone(zoneName, player):
            if card.name == cardName:
                return True
        return False

    def addCard(self, card, zoneName, player=-1):
        zone = self.getZone(zoneName, player)
        newCard = Card(card, len(self.cards), zoneName, player)
        self.cards.append(newCard)
        zone.append(newCard)

    def moveCards(self, cardList, src, dest, srcP=-1, destP=-1):
        srcZone = self.getZone(src, srcP)
        destZone = self.getZone(dest, destP)

        movedCards = []
        for cardName in cardList:
            moved = False
            for target in srcZone:
                if target.name == cardName:
                    srcZone.remove(target)
                    destZone.append(target)
                    target.move(dest)
                    target.player = self.player if destP == -1 else destP

                    moved = True
                    movedCards.append(target)
                    break
            if not moved:
                return False

        return movedCards

    def moveAllCards(self, src, dest, srcP=-1, destP=-1):
        srcZone = self.getZone(src, srcP)
        destZone = self.getZone(dest, destP)
        for card in srcZone:
            card.location = dest
            card.player = self.player if destP == -1 else destP

        destZone += srcZone
        srcZone.clear()
