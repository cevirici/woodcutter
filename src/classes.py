from copy import deepcopy
from .classes import *


class Exception:
    def __init__(self,
                 condition,
                 action,
                 priority=0,
                 persistent=True):

        self.condition = condition
        self.action = action
        self.name = repr(self)
        self.priority = priority
        self.persistent = persistent

    def __hash__(self):
        return self.name


class ParsedLine:
    def __init__(self, player, indent, pred, items, isCleanup=False):
        self.player = player
        self.indent = indent
        self.pred = pred
        self.predName = self.pred.name
        self.items = items
        self.isCleanup = isCleanup

    def __str__(self):
        return '{}{}{}{}'.format(self.player,
                                 self.indent,
                                 self.pred,
                                 self.items)

    def __repr__(self):
        return '{}{}{}{}'.format(hex(self.player)[2:],
                                 hex(self.indent)[2:],
                                 self.pred,
                                 self.items)


class Cardstack:
    # Stored as Card, but outside reference is via card name.
    # Cards are returned via cardList and getCards methods.
    def __init__(self, cards):
        self.cards = {}
        for c in cards:
            self.cards[Card[c]] = cards[c]

    def __iter__(self):
        for card in list(self.cards):
            yield str(card)

    def __getitem__(self, item):
        if Card[item] in self.cards:
            return self.cards[Card[item]]
        else:
            return 0

    def __setitem__(self, item, value):
        if item != 'ARGUMENT':
            self[item] = number
        else:
            if 'ARGUMENT' in self.cards:
                self.cards['ARGUMENT'] += '/' + str(number)
            else:
                self.cards['ARGUMENT'] = str(number)

    def __delitem__(self, item):
        if item in self:
            del self.cards[Card[item]]

    def __add__(self, other):
        t = deepcopy(self)
        for c in other:
            if c not in ['ARGUMENT', 'NOTHING', 'CARD']:
                if c in t:
                    t[c] += other[c]
                else:
                    t[c] = other[c]
        return t

    def __sub__(self, other):
        t = deepcopy(self)
        for c in other:
            if c not in ['ARGUMENT', 'NOTHING', 'CARD']:
                if c in t:
                    t[c] -= other[c]

        for c in t:
            if c in ['ARGUMENT', 'NOTHING', 'CARD'] or t[c] == 0:
                del t[c]
        return t

    def __gt__(self, other):
        return not(len(other - self) > 0)

    def __lt__(self, other):
        return not(len(self - other) > 0)

    def __str__(self):
        return '|'.join(['{}:{}'.format(self[i],
                                        str(Cards[i]))
                         for i in self.cards])

    def __repr__(self):
        return '|'.join(['{}:{}'.format(self[i],
                                        Cards[i])
                         for i in self.cards])

    def __len__(self):
        return sum([self[item] for item in self if item != 'ARGUMENT'])

    def cardList(self):
        return list(self.cards)

    def getCards(self):
        return self.cards

    def strip(self):
        t = deepcopy(self)
        for c in ['ARGUMENT', 'NOTHING', 'CARD']:
            del t[c]

        return t

    def primary(self):
        if len(self) > 0:
            return self[0]
        else:
            return 'CARD'

    def merge(self, target):
        t = deepcopy(self)
        for c in t:
            if c not in ['ARGUMENT', 'NOTHING']:
                if item in target:
                    t[c] = min(self[c], target[c])
                else:
                    del t[c]

        return t


gSZones = ('SUPPLY', 'DECKS', 'HANDS', 'INPLAYS',
           'DISCARDS', 'OTHERS', 'TRASH')
PERSONAL_ZONES = ('DECKS', 'HANDS', 'DISCARDS', 'OTHERS', 'INPLAYS')
gSLengths = (1, 2, 2, 2, 2, 2, 1)
gSQuantities = ('OBELISK', 'ACTIVE_PLAYER', 'INHERITED_CARDS',
                'VPS', 'VALID', 'PHASE')
quantityDefaults = (Card['CARD'],
                    0,
                    [Card['NOTHING'], Card['NOTHING']],
                    [0, 0],
                    True,
                    0)


class GameState:
    def __init__(self):
        self.boardState = {a: [Cardstack({}) for i in range(b)] for
                           a, b in zip(gSZones, gSLengths)}
        self.quantities = {a: b for a, b in
                           zip(gSQuantities, quantityDefaults)}

    def __getitem__(self, item):
        if item in self.boardState:
            (field, player) = item
            index = min(len(self.boardState[field]) - 1, player)
            return self.boardState[field][index]
        elif item in self.quantities:
            return self.quantities[item]
        else:
            raise KeyError

    def __setitem__(self, item, value):
        if item in self.boardState:
            (field, player) = item
            index = min(len(self.boardState[field]) - 1, player)
            self.boardState[field][index] = value
        elif item in self.quantities:
            self.quantities[item] = value
        else:
            raise KeyError

    def __str__(self):
        outstr = ''
        for zone in gSZones:
            outstr += '\n    ' + zone
            for part in self.boardState:
                outstr += '\n    ' + str(part)

        outstr += '\n    ------\n'
        return outstr

    def move(self, player, src, dest, items):
        itemsNoArgs = items.strip()
        if itemsNoArgs > self[(src, player)]:
            print('ILLEGAL MOVE {} from {} to {}'.format(items, src, dest))
            self['VALID'] = False

        self[(src, player)] -= itemsNoArgs
        self[(dest, player)] += itemsNoArgs

    def add(self, player, dest, items):
        self[(dest, player)] += items

    def crunch(self, zonelist, playerlist):
        outlist = Cardstack({})
        for zone in zonelist:
            if len(self.boardState[zone]) > 1:
                for player in playerlist:
                    outlist += self[(zone, player)]
            else:
                outlist += self[(zone, player)]

        return outlist

    def export(self):
        zoneStrings = [[repr(part) for part in self.boardState[zone]]
                       for zone in gSZones]
        return zoneStrings
