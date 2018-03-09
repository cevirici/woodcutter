from copy import deepcopy

#Constants
ARGUMENT_CARD = 0
NOTHING_CARD = 1
CARD_CARD = 2
GAMESTART_PRED = 0
NEWTURN_PRED = 1
SHUFFLE_PRED = 46
CLEANUP_PREDS = [21,46]
BOONHEX = range(373, 404)
standardCards = []

class Card:
    def __init__(self, simple_name, multi_name, phrase_name,
                 cost, supply_type, border_color, card_color, 
                 action, worth = lambda x,y: 0):

        self.simple_name = simple_name
        self.multi_name = multi_name
        self.phrase_name = phrase_name
        self.cost = cost
        self.supply_type = supply_type
        self.action = action
        self.border_color = border_color
        self.card_color = card_color
        self.worth = worth

    def names(self):
        return [self.simple_name, self.multi_name, self.phrase_name]

    def action(self, pred):
        self.action(pred)

class Exception:
    def __init__(self, condition, action, name='Exception'):
        self.condition = condition
        self.action = action
        self.name = name

    def __repr__(self):
        return self.name

class Pred:
    def __init__(self, regex, action, name):
        self.regex = regex
        self.action = action
        self.name = name

    def __repr__(self):
        return self.regex

class ParsedLine:
    def __init__(self, player, indent, pred, items):
        self.player = player
        self.indent = indent
        self.pred = pred
        self.items = items

    def __str__(self):
        return str(self.player)+str(self.indent)+str(self.pred)+str(self.items)

    def __repr__(self):
        return str(self.player)+str(self.indent)+str(self.pred)+str(self.items)

class Cardstack:
    def __init__(self,cards):
        self.val = cards

    def __add__(self,other):
        t = deepcopy(self.val)
        for c in other:
            if c != ARGUMENT_CARD:
                if c in t:
                    t[c] += other.val[c]
                else:
                    t[c] = other.val[c]
        return Cardstack(t)

    def __sub__(self,other):
        t = deepcopy(self.val)
        for c in other:
            if c != ARGUMENT_CARD:
                if c in t:
                    t[c] -= other.val[c]

        t = {c:v for c,v in t.items() if v > 0}
        return Cardstack(t)


    def __iter__(self):
        for card in list(self.val):
            yield card

    def insert(self, item, number):
        if item != ARGUMENT_CARD:
            if item in self.val:
                self.val[item] += number
            else:
                self.val[item] = number
        else:
            if item in self.val:
                self.val[item] += '/'+str(number)
            else:
                self.val[item] = str(number)


    def __str__(self):
        t = ['{}:{}'.format(self.val[i],hex(i)[2:]) for i in self.val]
        outstr = '|'.join(t)
        return outstr

    def __repr__(self):
        t = ['{}:{}'.format(self.val[i],hex(i)[2:]) for i in self.val]
        outstr = '|'.join(t)
        return outstr

    def __getitem__(self,item):
        return self.val[item]

    def count(self):
        return sum([self.val[item] for item in self.val])

    def cardList(self):
        return list(self.val)

    def getval(self):
        return self.val

class gameState:
    def __init__(self):
        self.SUPPLY = [Cardstack({})]
        self.DECKS = [Cardstack({}), Cardstack({})]
        self.HANDS = [Cardstack({}), Cardstack({})]
        self.INPLAYS = [Cardstack({}), Cardstack({})]
        self.DISCARDS = [Cardstack({}), Cardstack({})]
        self.OTHERS = [Cardstack({}), Cardstack({})]
        self.TRASH = [Cardstack({})]
        self.dontdiscard = [Cardstack({}), Cardstack({})]
        self.neverdiscard = [Cardstack({}), Cardstack({})]
        self.coins = [0, 0]
        self.coinsLower = [0, 0]
        self.vps = [0, 0]
        self.obelisk = []

    def __str__(self):
        outstr = ''
        for zone in ['SUPPLY','DECKS','HANDS','INPLAYS','DISCARDS','OTHERS','TRASH']:
            outstr +='\n    '+zone
            for part in getattr(self, zone):
                outstr += '\n    '+str(part)

        outstr += '\n    ------\n'
        return outstr

    def move(self, player, src, dest, items):
        itemsNoArgs = deepcopy(items)
        if ARGUMENT_CARD in items:
            del itemsNoArgs.val[ARGUMENT_CARD]
        if NOTHING_CARD in items:
            del itemsNoArgs.val[NOTHING_CARD]

        if len((itemsNoArgs - getattr(self, src)[min(len(getattr(self, src))-1, player)]).cardList()) > 0:
            print('ILLEGAL MOVE {} from {} to {}'.format(items, src, dest))

        getattr(self, src)[min(len(getattr(self, src))-1, player)] -= itemsNoArgs
        getattr(self, dest)[min(len(getattr(self, dest))-1, player)] += itemsNoArgs

    def add(self, player, dest, items):
        getattr(self, dest)[min(len(getattr(self, dest))-1, player)] += items

    def crunch(self, zonelist, playerlist):
        outlist = Cardstack({})
        for zone in zonelist:
            if len(getattr(self, zone)) > 1:
                for player in playerlist:
                    outlist += getattr(self, zone)[player]
            else:
                outlist += getattr(self, zone)[0]

        return outlist
