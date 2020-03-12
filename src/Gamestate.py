from .Card import *
from .Pile import *
from .Utils import *
PLAYER_COUNT = 2


class Gamestate:
    def __init__(self):
        self.player = 0
        self.turnNumber = 0
        self.turnType = TurnTypes.PREGAME
        self.zones = {z: [[] for p in range(PLAYER_COUNT)]
                      for z in PlayerZones}
        self.zones.update({z: [] for z in NeutralZones})

        self.resolutionStack = []
        self.logLine = 0
        self.candidates = []
        self.selectedMove = None

        self.actions = 0

        self.turnStartEffects = []
        self.cleanupEffects = []

    def zoneCount(self, zoneName, player=-1):
        if player == -1:
            player = self.player
        if isinstance(zoneName, PlayerZones):
            return sum([pile.count() for pile
                        in self.zones[zoneName][player]])
        else:
            return sum([pile.count() for pile in self.zones[zoneName]])

    def zoneContains(self, card, zoneName, player=-1):
        if player == -1:
            player = self.player
        if isinstance(zoneName, PlayerZones):
            zone = self.zones[zoneName][player]
        else:
            zone = self.zones[zoneName]

        for pile in zone:
            if pile.contains(card):
                return True
        return False

    def newPile(self, pile, zoneName, player=-1):
        if player == -1:
            player = self.player
        if isinstance(zoneName, PlayerZones):
            self.zones[zoneName][player].append(pile)
        else:
            self.zones[zoneName].append(pile)

    def add(self, card, zone, keyCard=None):
        # Adds a card to a zone
        if len(zone) == 0:
            zone.append(Pile(keyCard if keyCard else card, []))
        zone[0].addCard(card)

    def addCard(self, card, zoneName, keyCard=None, player=0):
        # This doesn't care about piles. If there isn't a pile, make a pile.
        if isinstance(zoneName, PlayerZones):
            zone = self.zones[zoneName][player]
        else:
            zone = self.zones[zoneName]
        self.add(card, zone, keyCard)

    def addToSupply(self, card, zoneName):
        # This one cares about piles
        # This shouldn't be called on playerzones so player is not a param
        for pile in self.zones[zoneName]:
            if (card in pile.acceptedCards):
                pile.addCard(card)
                return

    def moveCards(self, cardList, src, dest, srcP=-1, destP=-1):
        cardList = copy(cardList)
        if isinstance(src, PlayerZones):
            if srcP >= 0:
                srcZone = self.zones[src][srcP]
            else:
                srcZone = self.zones[src][self.player]
        else:
            srcZone = self.zones[src]

        if isinstance(dest, PlayerZones):
            if destP >= 0:
                destZone = self.zones[dest][destP]
            else:
                destZone = self.zones[dest][self.player]
        else:
            destZone = self.zones[dest]

        while cardList:
            removedSomething = False
            for card in cardList:
                for pile in srcZone:
                    if pile.contains(card):
                        pile.remove(card)
                        removedSomething = True
                        cardList.remove(card)
                        self.add(card, destZone)
                        # Avoid double removal
                        break
                if removedSomething:
                    # We need to break here as otherwise we'd mutate
                    # the list we're iterating in
                    break

            if not removedSomething:
                return False
        return True

    def moveAllCards(self, src, dest, srcP=-1, destP=-1):
        if isinstance(src, PlayerZones):
            if srcP >= 0:
                srcZone = self.zones[src][srcP]
            else:
                srcZone = self.zones[src][self.player]
        else:
            srcZone = self.zones[src]

        if isinstance(dest, PlayerZones):
            if destP >= 0:
                destZone = self.zones[dest][destP]
            else:
                destZone = self.zones[dest][self.player]
        else:
            destZone = self.zones[dest]

        for pile in srcZone:
            for card in pile.cards:
                self.add(card, destZone)
            pile.removeAll()

        return True
