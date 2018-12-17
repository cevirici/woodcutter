from .standards import *


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
                                 repr(self.items))


gSZones = ('SUPPLY', 'DECKS', 'HANDS', 'INPLAYS',
           'DISCARDS', 'OTHERS', 'TRASH')
PERSONAL_ZONES = ('DECKS', 'HANDS', 'DISCARDS', 'OTHERS', 'INPLAYS')
gSLengths = (1, 2, 2, 2, 2, 2, 1)
gSQuantities = ('OBELISK', 'ACTIVE_PLAYER', 'INHERITED_CARDS',
                'VPS', 'VALID', 'PHASE')
quantityDefaults = ([],
                    0,
                    [Cards['NOTHING'], Cards['NOTHING']],
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
        if type(item) == tuple:
            (field, player) = item
            if field in self.boardState:
                index = min(len(self.boardState[field]) - 1, player)
                return self.boardState[field][index]
            else:
                raise KeyError
        elif item in self.quantities:
            return self.quantities[item]
        else:
            raise KeyError

    def __setitem__(self, item, value):
        if type(item) == tuple:
            (field, player) = item
            if field in self.boardState:
                index = min(len(self.boardState[field]) - 1, player)
                self.boardState[field][index] = value
            else:
                raise KeyError
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
