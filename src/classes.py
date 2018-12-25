from .Standards import *
from .Cardstack import *
from copy import deepcopy


class ParsedLine:
    def __init__(self, indent, pred, players,
                 items, arguments, isCleanup=False):
        self.indent = indent
        self.pred = pred
        self.predName = self.pred.name
        self.items = items
        self.players = players
        self.arguments = arguments
        self.isCleanup = isCleanup

    def __repr__(self):
        playerStr = '/'.join([str(x) for x in self.players])
        itemStr = '/'.join([repr(x) for x in self.items])
        return '{}|{}|{}|{}|{}'.format(self.indent,
                                       repr(self.pred),
                                       playerStr,
                                       itemStr,
                                       '/'.join(self.arguments))

    @property
    def player(self):
        return self.players[0]


class GameState:
    playerZones = ('DECKS', 'HANDS', 'INPLAYS', 'DISCARDS', 'TAVERN', 'OTHERS')
    soloZones = ('SUPPLY', 'TRASH')

    def __init__(self, players=2):
        self.boardState = {}
        for zone in GameState.playerZones:
            self.boardState[zone] = [Cardstack({}) for i in range(players)]
        for zone in GameState.soloZones:
            self.boardState[zone] = Cardstack({})

        self.activePlayer = -1
        self.obelisk = []
        self.coins = 0
        self.actions = 0
        self.buys = 0
        self.inherited = ['NOTHING', 'NOTHING']
        self.vps = [0, 0]
        self.coffers = [0, 0]
        self.villagers = [0, 0]
        self.debt = [0, 0]
        self.phase = 0  # Start, Action, Buy, Night, Cleanup
        self.exceptions = set()
        self.durations = [[], []]
        self.linkedPlays = []  # list: plays, cards, currentDurations
        self.amuletSilvers = 0
        self.cargoShips = 0
        self.cargoCount = 0

        self.valid = True

    def __getitem__(self, item):
        return self.boardState[item]

    def __setitem__(self, item, value):
        self.boardState[item] = value

    def __str__(self):
        basestr = '\
Player: {}<br>\
Phase: {}<br>\
C: {} A: {} B: {}<br>\
vp: {}<br> co: {}<br> vi: {}<br> db: {}<br>\
Score: {}<br>'
        outstr = basestr.format(self.activePlayer, self.phase, self.coins,
                                self.actions, self.buys,
                                ','.join([str(x) for x in self.vps]),
                                ','.join([str(x) for x in self.coffers]),
                                ','.join([str(x) for x in self.villagers]),
                                ','.join([str(x) for x in self.debt]),
                                ', '.join([str(x) for x in self.score]))
        outstr += 'Cards:<br>'
        for zone in self.boardState:
            outstr += '<br>    ' + zone
            if zone in GameState.playerZones:
                for part in self.boardState[zone]:
                    outstr += '<br>    ' + str(part) + '<br>'
            else:
                outstr += '<br>    ' + str(self.boardState[zone]) + '<br>'

            outstr += '---'

        outstr += '<br>    ------<br>'
        return outstr

    def move(self, player, src, dest, items):
        items = items.strip()
        if src in GameState.soloZones:
            if items > self[src]:
                self.valid = False
            self[src] -= items
        else:
            if items > self[src][player]:
                self.valid = False
            self[src][player] -= items

        if dest in GameState.soloZones:
            self[dest] += items
        else:
            self[dest][player] += items

    def add(self, dest, items, player=0):
        if dest in GameState.soloZones:
            self[dest] += items
        else:
            self[dest][player] += items

    def crunch(self, zonelist, playerlist):
        outlist = Cardstack({})
        for zone in zonelist:
            if zone in GameState.playerZones:
                for player in playerlist:
                    outlist += self[zone][player]
            else:
                outlist += self[zone]

        return outlist

    @property
    def score(self):
        output = []
        for player in range(len(self['DECKS'])):
            playerDeck = self.crunch(GameState.playerZones, [player])
            output.append(sum([Cards[card].worth(self, player) *
                               playerDeck[card]
                               for card in playerDeck]))
        return output

    def export(self):
        zoneStrings = [[repr(part) for part in self.boardState[zone]]
                       for zone in gSZones]
        return zoneStrings
