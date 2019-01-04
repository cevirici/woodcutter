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
        return self.players[0] if self.players else 0


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
        self.projects = [set(), set()]
        self.vps = [0, 0]
        self.coffers = [0, 0]
        self.villagers = [0, 0]
        self.debt = [0, 0]
        self.bridges = 0
        self.phase = 0  # Start, Action, Buy, Night, Cleanup

        self.exceptions = []
        self.durations = [[], []]
        self.linkedPlays = []  # list: plays, cards, currentDurations

        self.amuletSilvers = 0
        self.cargoShips = 0
        self.cargoCount = 0
        self.orderedPlays = []

        self.valid = True

    def __getitem__(self, item):
        return self.boardState[item]

    def __setitem__(self, item, value):
        self.boardState[item] = value

    def __repr__(self):
        outstr = ''
        for zone in self.boardState:
            if zone in GameState.playerZones:
                for part in self.boardState[zone]:
                    outstr += repr(part) + '|'
            else:
                outstr += repr(self.boardState[zone]) + '|'
        outstr += '/'
        outstr += '|'.join([str(self.actions), str(self.buys), str(self.coins),
                            *[str(x) for x in self.debt],
                            *[str(x) for x in self.coffers],
                            *[str(x) for x in self.villagers],
                            *[str(x) for x in self.vps]])
        return outstr

    def __str__(self):
        basestr = '{}<br>\
Player: {}<br>\
Phase: {}<br>\
C: {} A: {} B: {}<br>\
vp: {}<br> co: {}<br> vi: {}<br> db: {}<br>\
Score: {}<br>'
        outstr = basestr.format(str(self.valid), self.activePlayer,
                                len(self.exceptions),
                                self.coins, self.actions, self.buys,
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
            if not self[src] > items:
                self.valid = False
            self[src] -= items
        else:
            if not self[src][player] > items:
                self.valid = False
            self[src][player] -= items

        if dest in GameState.soloZones:
            self[dest] += items
        else:
            self[dest][player] += items

        # Edit orderedinplays
        if src == 'INPLAYS':
            for card in items:
                for i in range(items[card]):
                    if card in self.orderedPlays:
                        self.orderedPlays.remove(card)

        if dest == 'INPLAYS':
            for card in items:
                for i in range(items[card]):
                    self.orderedPlays.append(card)

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

    def export(self):
        zoneStrings = [[repr(part) for part in self.boardState[zone]]
                       for zone in gSZones]
        return zoneStrings

    def empty_piles(self, supply):
        pairs = {'ENCAMPMENT': ['ENCAMPMENT', 'PLUNDER'],
                 'PATRICIAN': ['PATRICIAN', 'EMPORIUM'],
                 'SETTLERS': ['SETTLERS', 'BUSTLING VILLAGE'],
                 'CATAPULT': ['CATAPULT', 'ROCKS'],
                 'GLADIATOR': ['GLADIATOR', 'FORTUNE'],
                 'KNIGHTS': ['DAME ANNA', 'DAME JOSEPHINE', 'DAME MOLLY',
                             'DAME NATALIE', 'DAME SYLVIA', 'SIR BAILEY',
                             'SIR DESTRY', 'SIR MARTIN', 'SIR MICHAEL',
                             'SIR VANDER'],
                 'RUINS': ['RUINED LIBRARY', 'RUINED VILLAGE',
                           'ABANDONED MINE', 'RUINED MARKET', 'SURVIVORS'],
                 'SAUNA': ['SAUNA', 'AVANTO'],
                 'CASTLES': ['HUMBLE CASTLE', 'CRUMBLING CASTLE',
                             'SMALL CASTLE', 'HAUNTED CASTLE',
                             'OPULENT CASTLE', 'SPRAWLING CASTLE',
                             'GRAND CASTLE', "KING'S CASTLE"]}
        output = []
        for card in supply:
            if card in pairs:
                if sum([self['SUPPLY'][subcard]
                        for subcard in pairs[card]]) == 0:
                    output.append(card)
            elif self['SUPPLY'][card] == 0:
                output.append(card)
        return '|'.join([str(Cards[card].index) for card in output])
