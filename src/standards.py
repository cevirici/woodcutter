from .lists import *
from copy import deepcopy
from django.conf import settings
import os

CARD_URLS_PATH = 'woodcutter/card_images/imageurls.txt'

cardUrls = {}
f = open(os.path.join(settings.STATIC_ROOT, CARD_URLS_PATH))
for line in f:
    raw = line.strip().split(':')
    raw[1] = 'woodcutter/card_images/{}'.format(raw[1][raw[1].rfind('/') + 1:])
    cardUrls[raw[0]] = raw[1]


class Exception:
    def __init__(self,
                 condition,
                 action,
                 priority=0,
                 persistent=True):
        self.condition = condition
        self.action = action
        self.priority = priority
        self.persistent = persistent


class Card:
    def __init__(self, index, simple_name, multi_name, phrase_name,
                 cost, supply_type, border_color, card_color,
                 action, worth=lambda x, y: 0):

        self.index = index
        self.simple_name = simple_name
        self.multi_name = multi_name
        self.phrase_name = phrase_name
        self.names = [self.simple_name, self.multi_name, self.phrase_name]
        self.cost = cost
        self.supply_type = supply_type
        self.action = action
        self.border_color = border_color
        self.card_color = card_color
        self.worth = worth

        if self.simple_name in cardUrls:
            self.cardurl = cardUrls[self.simple_name]
        else:
            self.cardurl = cardUrls['card']

    def __repr__(self):
        return '{:0>3}'.format(hex(self.index)[2:])

    def __str__(self):
        return self.simple_name.upper()

    def __hash__(self):
        return self.index

    def __eq__(self, other):
        if type(other) == str:
            return self.simple_name == other
        else:
            return self.index == other.index


class Pred:
    def __init__(self, index, regex, action, name):
        self.index = index
        self.regex = regex
        self.action = action
        self.name = name

    def __repr__(self):
        return '{:0>2}'.format(hex(self.index)[2:])

    def __str__(self):
        return self.name

    def __hash__(self):
        return self.index

    def __eq__(self, other):
        if type(other) == str:
            return self.name == other
        else:
            return self.index == other.index


def empty(move, i, bL, moves, cS):
    return {}


def staticWorth(val):
    def out_function(gS, player):
        return val
    return out_function


Cards = {}
CardList = []
Preds = {}
PredList = []


class Cardstack:
    # Stored as Card, but outside reference is via card name.
    # Cards are returned via cardList and getCards methods.
    def __init__(self, cards):
        self.cards = {}
        for c in cards:
            self.cards[Cards[c]] = cards[c]

    def __iter__(self):
        for card in list(self.cards):
            yield str(card)

    def __getitem__(self, item):
        if Cards[item] in self.cards:
            return self.cards[Cards[item]]
        else:
            return '' if item == 'ARGUMENT' else 0

    def __setitem__(self, item, value):
        if item != 'ARGUMENT':
            self.cards[Cards[item]] = value
        else:
            if 'ARGUMENT' in self.cards:
                self.cards[Cards['ARGUMENT']] += '/' + str(value)
            else:
                self.cards[Cards['ARGUMENT']] = str(value)

    def __delitem__(self, item):
        if item in self:
            del self.cards[Cards[item]]

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
            if c in ['ARGUMENT', 'NOTHING', 'CARD'] or t[c] <= 0:
                del t[c]
        return t

    def __gt__(self, other):
        return not(len(other - self) > 0)

    def __lt__(self, other):
        return not(len(self - other) > 0)

    def __str__(self):
        return '|'.join(['{}:{}'.format(self[i], str(Cards[i]))
                         for i in self])

    def __repr__(self):
        return '|'.join(['{}:{}'.format(self[i], repr(Cards[i]))
                         for i in self])

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
            return list(self.cards.keys())[0]
        else:
            return 'CARD'

    def merge(self, target):
        t = deepcopy(self)
        for c in t:
            if c not in ['ARGUMENT', 'NOTHING']:
                if c in target:
                    t[c] = min(self[c], target[c])
                else:
                    del t[c]

        return t


cardFile = open(os.path.join(settings.STATIC_ROOT,
                             'woodcutter/data/carddata.txt'), 'r')
for i, line in enumerate(cardFile):
    t = line.strip().split(',')
    c = Card(i, *t[1:8], empty)
    if len(t) > 8:
        c.worth = staticWorth(int(t[8]))

    Cards[t[1].upper()] = c
    CardList.append(c)

cardFile.close()

predFile = open(os.path.join(settings.STATIC_ROOT,
                             'woodcutter/data/preddata.txt'), 'r')
for line in predFile:
    t = line.strip().split('~')
    p = Pred(int(t[0], 16), t[1], empty, t[2])
    Preds[t[2]] = p
    PredList.append(p)

predParseOrder = deepcopy(PredList)
PredList.sort(key=lambda p: p.index)

predFile.close()

PLAY_PREDS = ('PLAY', 'PLAY AGAIN', 'PLAY THIRD', 'PLAY CITADEL',
              'PLAY COIN', 'THRONE COIN')
GAIN_PREDS = ('GAIN', 'BUY AND GAIN', 'GAIN TOPDECK', 'GAIN TRASH')


def findRemainingSteps(i, moves):
    for c in range(len(moves) - i):
        if str(moves[c + i].pred) == "NEW TURN":
            return c
    return len(moves) - i


# -- Standard Exceptions -- #

def check(predList, targetList=[]):
    def out_function(move):
        if predList:
            if str(move.pred) not in predList:
                return False

        if targetList:
            if len([t for t in targetList if (t in move.items)]) == 0:
                return False
        return True

    return out_function


def transfer(src, dest, move, cS):
    if len(move.items) > 0:
        cS.move(move.player, src, dest, move.items)
    return {}


def moveFunct(src, dest):
    def out_function(move, i, bL, moves, cS):
        transfer(src, dest, move, cS)
        return {}
    return out_function


def checkMove(predList, src, dest, targetList=[]):
    return Exception(check(predList, targetList),
                     moveFunct(src, dest))


def gainCash(amount):
    def out_function(move, i, bL, moves, cS):
        cS['COINS'][move.player] += amount
        return {}

    return out_function


def onGains(src):
    def wasGained(predList):
        def out_function(move):
            if str(move.pred) not in predList:
                return False
            return gainedCards > move.items
        return out_function

    def villaExcAction(move, i, bL, moves, cS):
        transfer(src, 'HANDS', moves, cS)
        cS['PHASE'] = 0
        return {}

    villaException = Exception(check(['PUT INHAND'], ['VILLA']),
                               villaExcAction)

    def out_function(move, i, bL, moves, cS):
        newExcs = {}
        gainedCards = move.items

        if 'VILLA' in gainedCards:
            newExcs[villaException] = bL

        for scan in moves[i + 1: i + bL]:
            if str(scan.pred) == "REVEAL" and \
               scan.items.primary() == 'WATCHTOWER':
                for exc in [Exception(wasGained(['TOPDECK']),
                                      moveFunct(src, 'DECKS')),
                            Exception(wasGained(['TRASH']),
                                      moveFunct(src, 'TRASH'))]:
                    newExcs[exc] = bL
                break

        newExcs[Exception(wasGained(['RETURN']),
                          moveFunct(src, 'SUPPLY'))] = bL
        return newExcs

    return out_function


def onPlay(move, i, bL, moves, cS):
    for card in move.items.strip():
        for i in range(move.items[card]):
            return Cards[card].action(move, i, bL, moves, cS)


def onTrash(move, i, bL, moves, cS):
    for card in move.items.strip():
        for i in range(move.items[card]):
            return Cards[card].action(move, i, bL, moves, cS)


exc_revealTrash = checkMove(['TRASH'], 'DECKS', 'TRASH')
exc_revealTopdeck = checkMove(['TOPDECK'], 'DECKS', 'DECKS')
exc_revealDiscard = checkMove(['DISCARD'], 'DECKS', 'DISCARDS')
exc_harbinger = checkMove(['TOPDECK'], 'DISCARDS', 'DECKS')
exc_gainHand = checkMove(['GAIN'], 'SUPPLY', 'HANDS')
exc_supplyTrash = checkMove(['TRASH'], 'SUPPLY', 'TRASH')
exc_inplayTrash = checkMove(['TRASH'], 'INPLAYS', 'TRASH')
exc_standardTrash = Exception(check(['TRASH']), onTrash)


# -- Standard Actions -- #


def deckchuck(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        return {exc_revealDiscard: bL}


def harbingerlike(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        return {exc_harbinger: bL}


def decksifter(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        return {exc: bL for exc in [exc_revealTopdeck, exc_revealDiscard]}


def selftrasher(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        return {exc: bL for exc in [exc_inplayTrash, exc_standardTrash]}


def sentrylike(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        return {exc: bL for exc in [exc_revealTrash,
                                    exc_standardTrash,
                                    exc_revealDiscard,
                                    exc_revealTopdeck]}


def banditlike(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        return {exc: bL for exc in [exc_revealTrash,
                                    exc_standardTrash,
                                    exc_revealDiscard]}


def golemlike(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        playExc = checkMove(['PLAY'], 'DECKS', 'INPLAYS')
        onPlayExc = Exception(check(['PLAY']), standardOnPlay)
        return {exc: bL for exc in [playExc, onPlayExc, exc_revealDiscard]}


def deckGain(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        gainExc = checkMove(['GAIN'], 'SUPPLY', 'DECKS')
        onGainExc = Exception(check(['GAIN']), onGains('DECKS'))
        return {exc: bL for exc in [gainExc, onGainExc]}


def emulate(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        playExc = checkMove(['PLAY'], 'SUPPLY', 'SUPPLY')
        onPlayExc = Exception(check(['PLAY']), standardOnPlay)
        return {exc: bL for exc in [playExc, onPlayExc]}


def standardReserve(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        return {checkMove(['PUT ONTO'], 'INPLAYS', 'OTHERS'): bL}


def discardToHand(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        return {checkMove(['PUT INHAND'], 'DISCARDS', 'HANDS'): bL}

# -- Individual Cards -- #


def estate_action(move, i, bL, moves, cS):
    return cS['INHERITED_CARDS'][move.player].action(move, i, bL, moves, cS)


Cards['ESTATE'].action = estate_action


def artisan_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        onGainExc = Exception(check(['GAIN']), onGains('HANDS'))
        return {exc_gainHand: bL, onGainExc: bL}


Cards['ARTISAN'].action = artisan_action

Cards['BANDIT'].action = banditlike


def bureaucrat_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        onGainExc = Exception(check(['GAIN']), onGains('DECKS'))
        gainExc = checkMove(['GAIN'], 'SUPPLY', 'DECKS', ['Silver'])
        return {exc: bL for exc in [onGainExc, gainExc]}


Cards['BUREAUCRAT'].action = bureaucrat_action


def gardens_worth(gS, player):
    return gS.crunch(PERSONAL_ZONES, (player)).count() // 10


Cards['GARDENS'].worth = gardens_worth

Cards['HARBINGER'].action = harbingerlike


def library_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        setAsideExc = checkMove(['SETS ASIDE WITH'], 'DECKS', 'OTHERS')
        libDiscardExc = checkMove(['DISCARD'], 'OTHERS', 'DISCARDS')
        return {exc: bL for exc in [setAsideExc, libDiscardExc]}


Cards['LIBRARY'].action = library_action


def mine_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        onGainExc = Exception(check(['GAIN']), onGains('HANDS'))
        return {exc: bL for exc in [exc_gainHand, onGainExc]}


Cards['MINE'].action = mine_action

Cards['SENTRY'].action = sentrylike


def vassal_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        outputExcs = {exc_revealDiscard: bL}

        for scan in moves[i + 1: i + bL]:
            if str(scan.pred) == 'DISCARD':
                discardedCard = str(scan.primary())
                vassalCheck = check(['PLAY'], [discardedCard])
                playExc = Exception(vassalCheck, move('DISCARDS', 'INPLAYS'))
                actionExc = Exception(vassalCheck, onPlay)
                outputExcs.update({playExc: bL, actionExc: bL})
                break

        return outputExcs


Cards['VASSAL'].action = vassal_action


# 40: Diplomat
def diplomat_action(move, i, bL, moves, cS):
    if str(move.pred) in ['REACT']:
        return {checkMove(['DISCARD'], 'HANDS', 'DISCARDS'): bL}


Cards['DIPLOMAT'].action = diplomat_action


def duke_worth(gS, player):
    playerDeck = gS.crunch(PERSONAL_ZONES, (player))
    return playerDeck['DUCHY']


Cards['DUKE'].worth = duke_worth


def lurker_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        return {exc: bL for exc in [exc_supplyTrash,
                                    exc_standardTrash,
                                    checkMove(['GAIN'], 'TRASH', 'DISCARDS'),
                                    Exception(check(['GAIN']),
                                              onGains('DISCARDS'))
                                    ]}


Cards['LURKER'].action = lurker_action


def mv_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        def delayedTrashCondition(move):
            return move.indent == 0 and \
                str(move.pred) == 'TRASH' and \
                move.items.primary() == 'MINING VILLAGE'

        trashExc = checkMove(['TRASH'], 'INPLAYS', 'TRASH', ['MINING VILLAGE'])
        if move.indent == 0:
            delayedTrash = Exception(delayedTrashCondition,
                                     moveFunct('INPLAYS', 'TRASH'))
            return {trashExc: bL, delayedTrash: bL + 1}
        else:
            return {trashExc: bL}


Cards['MINING VILLAGE'].action = mv_action


def patrol_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        return{exc_revealTopdeck: bL}


Cards['PATROL'].action = patrol_action


def replace_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        for scan in moves[i + 1: i + bL]:
            if str(scan) == 'GAIN' and scan.player == move.player:
                gainedCard = scan.items.primary()
                gainedStack = Cardstack({gainedCard: 1})

                def topdeckGainedCard(move, i, bL, moves, cS):
                    cS.move(move.player, 'DISCARDS', 'DECKS', gainedStack)

                return {Exception(check(['TOPDECK']), topdeckGainedCard): bL}


Cards['REPLACE'].action = replace_action

Cards['SWINDLER'].action = banditlike


def torturer_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        gainExc = checkMove(['GAIN'], 'SUPPLY', 'HANDS', ['Curse'])
        onGainExc = Exception(check(['GAIN'], ['Curse']),
                              onGains('HANDS'))
        return {exc: bL for exc in [gainExc, onGainExc]}


Cards['TORTURER'].action = torturer_action


def tradepost_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        onGainExc = Exception(check(['GAIN'], ['Silver']),
                              onGains('HANDS'))
        gainExc = checkMove(['GAIN'], 'SUPPLY', 'HANDS', ['Silver'])
        return {exc: bL for exc in [onGainExc, gainExc]}


Cards['TRADING POST'].action = tradepost_action


def ambassador_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        return {checkMove(['RETURN TO'], 'HANDS', 'SUPPLY'): bL}


Cards['AMBASSADOR'].action = ambassador_action

Cards['EMBARGO'].action = selftrasher


def explorer_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        onGainExc = Exception(check(['GAIN'], ['Silver', 'Gold']),
                              onGains('HANDS'))
        gainExc = checkMove(['GAIN'], 'SUPPLY', 'HANDS', ['Silver', 'Gold'])
        return {exc: bL for exc in [onGainExc, gainExc]}


Cards['EXPLORER'].action = explorer_action


def island_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        islandStack = Cardstack({"ISLAND": 1})
        otherStuff = move.items - islandStack

        def islandSetaside(islandStack, otherStuff):
            def out_function(move, i, bL, moves, cS):
                cS.transfer(move.player, 'INPLAYS', 'OTHERS', islandStack)
                cS.transfer(move.player, 'HANDS', 'OTHERS', otherStuff)
            return out_function

        return {Exception(check(['PUT ONTO']),
                          islandSetaside(islandStack, otherStuff)): bL}


Cards['ISLAND'].action = island_action

Cards['LOOKOUT'].action = sentrylike


def nv_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        pullExc = checkMove(['PUT INHAND'], 'OTHERS', 'HANDS')
        setExc = checkMove(['SET ASIDE WITH'], 'DECKS', 'OTHERS')
        return {exc: bL for exc in [pullExc, setExc]}


Cards['NATIVE VILLAGE'].action = nv_action

Cards['NAVIGATOR'].action = decksifter


def pearldiver_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        return {checkMove(['TOPDECK'], 'DECKS', 'DECKS'): bL}


Cards['PEARL DIVER'].action = pearldiver_action

Cards['PIRATE SHIP'].action = banditlike


def seahag_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        gainExc = checkMove(['GAIN'], 'SUPPLY', 'DECKS', ['CURSE'])
        onGainExc = Exception(check(['GAIN'], ['CURSE']),
                              onGains('DECKS'))
        return {exc: bL for exc in [exc_revealDiscard, gainExc, onGainExc]}


Cards['SEA HAG'].action = seahag_action


def tmap_action(move, i, bL, moves, cS):
    def tmap_one(cM):
        if str(move.pred) == 'TRASH':
            if move.items['TREASURE MAP'] == 1:
                return True
        return False

    def tmap_two(cM):
        if str(move.pred) == 'TRASH':
            if move.items['TREASURE MAP'] == 2:
                return True
        return False

    def tmap_double_trash(move, i, bL, moves, cS):
        single_map = Cardstack({'TREASURE MAP': 1})
        cS.transfer(move.player, 'INPLAYS', 'TRASH', single_map)
        cS.transfer(move.player, 'HANDS', 'TRASH', single_map)

    if str(move.pred) in PLAY_PREDS:
        return {Exception(tmap_one, moveFunct('INPLAYS', 'TRASH')): bL,
                Exception(tmap_two, tmap_double_trash): bL}


Cards['TREASURE MAP'].action = tmap_action


def apoth_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        return {exc_revealTopdeck: bL}


Cards['APOTHECARY'].action = apoth_action

Cards['GOLEM'].action = golemlike


def herbalist_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        return {checkMove(['TOPDECK'], 'INPLAYS', 'DECKS'): bL}


Cards['HERBALIST'].action = herbalist_action

Cards['SCRYING POOL'].action = decksifter


def vineyard_worth(gS, player):
    playerDeck = gS.crunch(PERSONAL_ZONES, (player))
    return sum([playerDeck[item] for item in playerDeck if
                item in actionList]) // 3


Cards['VINEYARD'].worth = vineyard_worth


def countinghouse_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        return {checkMove(['PUT INHAND'], 'DISCARDS', 'HANDS'): bL}


Cards['COUNTING HOUSE'].action = countinghouse_action

Cards['LOAN'].action = banditlike


def mint_action(move, i, bL, moves, cS):
    if str(move.pred) in ['BUY AND GAIN', 'BUY']:
        return {checkMove(['TRASH'], 'INPLAYS', 'TRASH'): bL}


Cards['MINT'].action = mint_action

Cards['RABBLE'].action = decksifter

Cards['VENTURE'].action = golemlike


def bagofgold_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        gainExc = checkMove(['GAIN'], 'SUPPLY', 'DECKS', ['GOLD'])
        onGainExc = Exception(check(['GAIN'], ['GOLD']),
                              onGains('DECKS'))
        return {exc: bL for exc in [gainExc, onGainExc]}


Cards['BAG OF GOLD'].action = bagofgold_action


def fairgrounds_worth(gS, player):
    playerDeck = gS.crunch(PERSONAL_ZONES, (player))
    return len(playerDeck.cardList()) // 5


Cards['FAIRGROUNDS'].worth = fairgrounds_worth


def farmvillage_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        return {exc_revealDiscard: bL}


Cards['FARMING VILLAGE'].action = deckchuck

Cards['FORTUNE TELLER'].action = decksifter

Cards['HARVEST'].action = deckchuck


def horseTraders_action(move, i, bL, moves, cS):
    if str(move.pred) == 'REACT':
        return {checkMove(['SET ASIDE'], 'HANDS', 'OTHERS',
                          ['HORSE TRADERS']): 2}


Cards['HORSE TRADERS'].action = horseTraders_action


def hop_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        return {checkMove(['TRASH'], 'INPLAYS', 'TRASH',
                          ['HORN OF PLENTY']): bL}


Cards['HORN OF PLENTY'].action = hop_action

Cards['HUNTING PARTY'].action = deckchuck

Cards['JESTER'].action = deckchuck

Cards['TOURNAMENT'].action = deckGain


def steed_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        onGainExc = Exception(check(['GAIN']), onGains('DECKS'))
        gainExc = checkMove(['GAIN'], 'SUPPLY', 'DECKS', ['Silver'])
        return {exc: bL for exc in [onGainExc, gainExc]}


Cards['TRUSTY STEED'].action = steed_action

Cards['CARTOGRAPHER'].action = decksifter

Cards['DEVELOP'].action = deckGain

Cards['DUCHESS'].action = decksifter


def fg_action(move, i, bL, moves, cS):
    if str(move.pred) in ['TRASH']:
        gainExc = checkMove(['GAIN'], 'SUPPLY', 'DECKS', ['GOLD'])
        onGainExc = Exception(check(['GAIN'], ['GOLD']),
                              onGains('DECKS'))
        return {exc: bL for exc in [gainExc, onGainExc]}


Cards["FOOL'S GOLD"].action = fg_action


def igg_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        gainExc = checkMove(['GAIN'], 'SUPPLY', 'HANDS', ['COPPER'])
        onGainExc = Exception(check(['GAIN'], ['COPPER']),
                              onGains('HANDS'))
        return {exc: bL for exc in [gainExc, onGainExc]}


Cards['ILL-GOTTEN GAINS'].action = igg_action

Cards['JACK OF ALL TRADES'].action = decksifter


def mandarin_action(move, i, bL, moves, cS):
    if str(move.pred) in GAIN_PREDS:
        return {checkMove(['TOPDECK'], 'INPLAYS', 'DECKS'): bL}


Cards['MANDARIN'].action = mandarin_action


def brigand_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS or str(move.pred) == 'BUY':
        return {exc: bL for exc in [exc_revealTrash,
                                    exc_standardTrash,
                                    exc_revealDiscard]}


Cards['NOBLE BRIGAND'].action = brigand_action

Cards['ORACLE'].action = decksifter


def silkroad_worth(gameState, player):
    playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
    return sum([playerDeck[item] for item in playerDeck if
                str(item) in victoryCards]) // 4


Cards['SILK ROAD'].worth = silkroad_worth

Cards['ARMORY'].action = deckGain

Cards['BAND OF MISFITS'].action = emulate


def beggar_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        gainExc = checkMove(['GAIN'], 'SUPPLY', 'HANDS', ['COPPER'])
        onGainExc = Exception(check(['GAIN'], ['COPPER']),
                              onGains('HANDS'))
        return {exc: bL for exc in [gainExc, onGainExc]}


Cards['BEGGAR'].action = beggar_action

Cards['CATACOMBS'].action = deckchuck

Cards['COUNTERFEIT'].action = selftrasher


def knightSuicide(knightPlayer):
    def out_function(move):
        isKnight = move.items.primary() in KNIGHTS
        return str(move.pred) == 'TRASH' and move.player == knightPlayer and \
            isKnight
    return out_function


def knightTrash(knightPlayer):
    def out_function(move):
        isKnight = move.items.primary() in KNIGHTS
        return str(move.pred) == 'TRASH' and move.player != knightPlayer and \
            isKnight
    return out_function


def knightAction(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(exc_revealDiscard)
        trashExc = Exception(knightsTrash(move.player),
                             moveFunct('DECKS', 'TRASH'))
        onTrashExc = Exception(knightsTrash(move.player),
                               standardOnTrash)
        suicideExc = Exception(knightsSuicide(move.player),
                               moveFunct('INPLAYS', 'TRASH'))
        return {exc: bL for exc in [exc_revealDiscard,
                                    trashExc,
                                    onTrashExc,
                                    suicideExc]}


def annaAction(move, i, bL, moves, cS):
    def annaTrash(knightPlayer):
        def out_function(move):
            trashPart = str(move.pred) == 'TRASH' and \
                move.items.primary() != 'DAME ANNA'
            return trashPart and move.player == knightPlayer
        return out_function

    if str(move.pred) in PLAY_PREDS:
        exc.append(exc_revealDiscard)
        trashExc = Exception(knightsTrash(move.player),
                             moveFunct('DECKS', 'TRASH'))
        onTrashExc = Exception(knightsTrash(move.player),
                               standardOnTrash)
        suicideExc = Exception(knightsSuicide(move.player),
                               moveFunct('INPLAYS', 'TRASH'))
        annaTrash = Exception(annaTrash(move.player),
                              moveFunct('HANDS', 'TRASH'))
        annaOnTrash = Exception(annaTrash(move.player),
                                standardOnTrash)
        return {exc: bL for exc in [exc_revealDiscard,
                                    trashExc,
                                    onTrashExc,
                                    suicideExc,
                                    annaTrash,
                                    annaOnTrash]}


def michaelAction(move, i, bL, moves, cS):
    def onReveal(l):
        def out_function(move, i, bL, moves, cS):
            return {exc_revealDiscard: l - 1}
        return out_function

    if str(move.pred) in PLAY_PREDS:
        michaelReveal = Exception(check(['REVEAL']), onReveal(bL))
        trashExc = Exception(knightsTrash(move.player),
                             moveFunct('DECKS', 'TRASH'))
        onTrashExc = Exception(knightsTrash(move.player),
                               standardOnTrash)
        suicideExc = Exception(knightsSuicide(move.player),
                               moveFunct('INPLAYS', 'TRASH'))
        return {exc: bL for exc in [michaelReveal,
                                    trashExc,
                                    onTrashExc,
                                    suicideExc]}


for knight in KNIGHTS:
    if knight == 'DAME ANNA':
        Cards[knight].action = annaAction
    elif knight == 'SIR MICHAEL':
        Cards[knight].action = michaelAction
    else:
        Cards[knight].action = knightAction


def deathcart_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        trashExc = checkMove(['TRASH'], 'INPLAYS', 'TRASH', ['DEATH CART'])
        onTrashExc = Exception(check(['TRASH'], ['DEATH CART']),
                               standardOnTrash)
        return {exc: bL for exc in [trashExc, onTrashExc]}


Cards['DEATH CART'].action = deathcart_action


def feodum_worth(gameState, player):
    playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
    return playerDeck['SILVER'] // 3


Cards['FEODUM'].worth = feodum_worth


def fortress_action(move, i, bL, moves, cS):
    if str(move.pred) == 'TRASH':
        return {checkMove(['PUT INHAND'], 'TRASH', 'HANDS'): bL}


Cards['FORTRESS'].action = fortress_action


def graverobber_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        for scan in moves[i + 1: i + bL]:
            if str(scan.pred) == 'TRASH':
                return {}
        else:
            gainExc = checkMove(['GAIN'], 'TRASH', 'DECKS')
            onGainExc = Exception(check(['GAIN']),
                                  onGains('DECKS'))
            return {exc: bL for exc in [gainExc, onGainExc]}


Cards['GRAVEROBBER'].action = graverobber_action


def hermit_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        playerDiscard = cS[('DISCARDS', move.player)]

        def discardTrash(playerDiscard):
            def out_function(move):
                return playerDiscard > move.items and str(move.pred) == 'TRASH'
            return out_function

        return {Exception(discardTrash(playerDiscard),
                          moveException('DISCARDS', 'TRASH')): bL}


Cards['HERMIT'].action = hermit_action

Cards['IRONMONGER'].action = decksifter

Cards['PILLAGE'].action = selftrasher

Cards['PROCESSION'].action = selftrasher

Cards['REBUILD'].action = banditlike


def rogue_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        rogueGain = checkMove(['GAIN'], 'TRASH', 'DISCARDS')
        rogueOnGain = Exception(check(['GAIN']),
                                standardOnGains('DISCARDS', move.items))
        return {exc: bL for exc in [exc_revealTrash,
                                    exc_standardTrash,
                                    exc_revealDiscard,
                                    rogueGain,
                                    rogueOnGain]}


Cards['ROGUE'].action = rogue_action

Cards['SAGE'].action = deckchuck

Cards['SCAVENGER'].action = harbingerlike

Cards['SURVIVORS'].action = decksifter

Cards['VAGRANT'].action = deckchuck

Cards['WANDERING MINSTREL'].action = decksifter

Cards['ADVISOR'].action = deckchuck

Cards['DOCTOR'].action = sentrylike


# 234: Herald
def herald_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        playExc = checkMove(['PLAY'], 'DECKS', 'INPLAYS')
        onPlayExc = Exception(check(['PLAY']), standardOnPlay)
        return {exc: bL for exc in [playExc, onPlayExc]}

    if str(move.pred) == 'BUY':
        return {exc_harbinger: bL}


Cards['HERALD'].action = herald_action

Cards['JOURNEYMAN'].action = deckchuck

Cards['TAXMAN'].action = deckGain

Cards['ARTIFICER'].action = deckGain


# 246: Bonfire
def bonfire_action(move, i, bL, moves, cS):
    if str(move.pred) == 'BUY':
        return {exc: bL for exc in [exc_inplayTrash, exc_standardTrash]}


Cards['BONFIRE'].action = bonfire_action

Cards['COIN OF THE REALM'].action = standardReserve


def distantlands_worth(gS, player):
    playerDeck = gS.crunch(['DECKS', 'OTHERS'], (player))
    total = playerDeck['DISTANT LANDS']

    return gS[('OTHERS', player)]['DISTANT LANDS'] / total


Cards['DISTANT LANDS'].worth = distantlands_worth

Cards['DUPLICATE'].action = standardReserve

Cards['GIANT'].action = banditlike

Cards['GUIDE'].action = standardReserve

Cards['MAGPIE'].action = decksifter

Cards['RATCATCHER'].action = standardReserve


def razeAction(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        razeExc = checkMove(['TRASH'], 'INPLAYS', 'TRASH', ['Raze'])
        return {exc: bL for exc in [razeExc, exc_revealDiscard]}


Cards['RAZE'].action = razeAction

Cards['ROYAL CARRIAGE'].action = standardReserve


def save_action(move, i, bL, moves, cS):
    if str(move.pred) == 'BUY':
        return {checkMove(['PUT INHAND'], 'OTHERS', 'HANDS'):
                findRemainingSteps(i, moves)}


Cards['SAVE'].action = save_action


def scoutingparty_action(move, i, bL, moves, cS):
    if str(move.pred) == 'BUY':
        return {exc: bL for exc in [exc_revealTopdeck, exc_revealDiscard]}


Cards['SCOUTING PARTY'].action = save_action

Cards['TEACHER'].action = standardReserve


def transmogrify_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        return {checkMove(['PUT ONTO'], 'INPLAYS', 'OTHERS'): bL}

    if str(move.pred) == 'CALL':
        gainExc = checkMove(['GAIN'], 'SUPPLY', 'HANDS')
        onGainExc = Exception(check(['GAIN']), onGains('HANDS'))
        for l in range(2, len(moves) - i):
            if moves[i + l].indent == 0:
                break
        return {exc: l for exc in [gainExc, onGainExc]}


Cards['TRANSMOGRIFY'].action = transmogrify_action


def warrior_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        return {exc: bL for exc in [checkMove(['TRASH'], 'DISCARDS', 'TRASH'),
                                    exc_standardTrash,
                                    exc_revealDiscard]}


Cards['WARRIOR'].action = transmogrify_action

Cards['WINE MERCHANT'].action = transmogrify_action

Cards['PATRICIAN'].action = decksifter

Cards['SETTLERS'].action = discardToHand

Cards['BUSTLING VILLAGE'].action = discardToHand


def rocks_action(move, i, bL, moves, cS):
    if str(move.pred) in GAIN_PREDS:
        if cS['PHASE'] == 1:
            gainExc = checkMove(['GAIN'], 'SUPPLY', 'DECKS')
            onGainExc = Exception(check(['GAIN']),
                                  onGains('DECKS'))
            return {exc: bL for exc in [gainExc, onGainExc]}
        else:
            gainExc = checkMove(['GAIN'], 'SUPPLY', 'HANDS')
            onGainExc = Exception(check(['GAIN']),
                                  onGains('HANDS'))
            return {exc: bL for exc in [gainExc, onGainExc]}


Cards['ROCKS'].action = rocks_action


def gladiator_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        return {checkMove(['TRASH'], 'SUPPLY', 'TRASH', ['GLADIATOR']): bL}


Cards['GLADIATOR'].action = gladiator_action

CASTLES = ['HUMBLE CASTLE', 'CRUMBLING CASTLE', 'SMALL CASTLE',
           'HAUNTED CASTLE', 'OPULENT CASTLE', 'SPRAWLING CASTLE',
           'GRAND CASTLE', 'KING\'S CASTLE']


def humbleCastle_worth(gS, player):
    playerDeck = gS.crunch(PERSONAL_ZONES, (player))
    return sum([playerDeck[item] for item in playerDeck if
                item in castles])


def kingsCastle_worth(gS, player):
    playerDeck = gS.crunch(PERSONAL_ZONES, (player))
    return 2 * sum([playerDeck[item] for item in playerDeck if
                    item in castles])


Cards['HUMBLE CASTLE'].worth = humbleCastle_worth


def smallcastle_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        return {checkMove(['TRASH'], 'INPLAYS', 'TRASH', ['SMALL CASTLE']): bL}


Cards['SMALL CASTLE'].worth = humbleCastle_worth

Cards["KING'S CASTLE"].worth = kingsCastle_worth


def archive_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        return {checkMove(['SET ASIDE'], 'DECKS', 'OTHERS'): bL}


Cards['ARCHIVE'].action = archive_action


def banditfort_worth(gameState, player):
    playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
    return sum([-2 * playerDeck[item] for item in playerDeck if
                item in ['SILVER', 'GOLD']])


Cards['BANDIT FORT'].worth = banditfort_worth

Cards['CHARIOT RACE'].action = decksifter


def engineer_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        def engineerTrashCondition(move):
            return move.indent == 0 and \
                str(move.pred) == 'TRASH' and \
                move.items.primary() == 'ENGINEER'

        trashExc = checkMove(['TRASH'], 'INPLAYS', 'TRASH', ['ENGINEER'])
        if move.indent == 0:
            delayedTrash = Exception(engineerTrashCondition,
                                     moveFunct('INPLAYS', 'TRASH'))
            return {trashExc: bL, delayedTrash: bL + 2}
        else:
            return {trashExc: bL}


Cards['ENGINEER'].action = engineer_action


def farmmarket_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        return {checkMove(['TRASH'], 'INPLAYS', 'TRASH', ["FARMERS' MARKET"])}


Cards["FARMERS' MARKET"].action = farmmarket_action


def fountain_worth(gameState, player):
    playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
    if playerDeck['COPPER'] >= 10:
        return 15
    return 0


Cards['FOUNTAIN'].worth = fountain_worth


def keep_worth(gameState, player):
    playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
    otherDeck = gameState.crunch(PERSONAL_ZONES, [1 - player])
    total = 0

    for card in playerDeck:
        if card in treasures:
            if playerDeck[card] >= otherDeck[card]:
                total += 5

    return total


Cards['KEEP'].worth = keep_worth


def museum_worth(gameState, player):
    playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
    return 2 * len(playerDeck.cardList())


Cards['MUSEUM'].worth = museum_worth


def obelisk_worth(gameState, player):
    playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
    return sum(playerDeck[c] for c in gameState['OBELISK'])


Cards['OBELISK'].worth = obelisk_worth


# 352: Orchard
def orchard_worth(gameState, player):
    playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
    total = 0

    for card in playerDeck:
        if card in actionList:
            if playerDeck[card] >= 3:
                total += 4

    return total


Cards['ORCHARD'].worth = orchard_worth

Cards['OVERLORD'].action = emulate


def palace_worth(gameState, player):
    playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
    treasures = ['COPPER', 'SILVER', 'GOLD']
    counts = [0, 0, 0]

    for card in treasures:
        counts[treasures.index(card)] = playerDeck[card]

    return 3 * min(counts)


Cards['PALACE'].worth = palace_worth


def salt_action(move, i, bL, moves, cS):
    if str(move.pred) == 'BUY':
        return{checkMove(['TRASH'], 'SUPPLY', 'TRASH'): bL}


Cards['SALT THE EARTH'].action = salt_action


def tower_worth(gameState, player):
    playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
    total = 0

    for card in playerDeck:
        if standardCards[card].supply_type == 0 and\
                card not in gameState[('SUPPLY', 0)]:
            if card not in victoryCards:
                total += playerDeck[card]

    return total


Cards['TOWER'].worth = tower_worth


def arch_worth(gameState, player):
    playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
    counts = sorted([playerDeck[card] for card in playerDeck if
                     card in actionList], reverse=True)
    counts = counts + [0, 0]

    return 3 * counts[1]


Cards['TRIUMPHAL ARCH'].worth = arch_worth


def wall_worth(gameState, player):
    playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
    return 15 - max(15, len(playerDeck))


Cards['WALL'].worth = wall_worth


def den_worth(gameState, player):
    playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
    return -3 * len([card for card in playerDeck if playerDeck[card] == 1])


Cards['WOLF DEN'].worth = den_worth


def miserable_action(move, i, bL, moves, cS):
    if str(move.pred) == ['TAKES']:
        cS.vps[move.player] -= 2


Cards['MISERABLE'].action = miserable_action

Cards['TWICE MISERABLE'].action = miserable_action

Cards['CHANGELING'].action = selftrasher


def druid_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        t = {Exception(check('RECEIVE BOONHEX'), empty): bL}
        for scan in moves[i + 1: i + bL]:
            if str(scan.pred) == 'RECEIVE BOONHEX':
                whichBoon = scan.items.primary()
                break

        if whichBoon == "THE SUN'S GIFT":
            t[exc_revealTopdeck] = bL
            t[exc_revealDiscard] = bL

        elif whichBoon == "THE MOON'S GIFT":
            t[exc_harbinger] = bL

        return t


Cards['DRUID'].action = druid_action


def hound_action(move, i, bL, moves, cS):
    if str(move.pred) in ['REACT']:
        return {checkMove(['SET ASIDE'], 'DISCARDS', 'OTHERS',
                          ['FAITHFUL HOUND']): 2}


Cards['FAITHFUL HOUND'].action = hound_action


def monastery_action(move, i, bL, moves, cS):
    # Possible conflicts: Exorcist - hence, trash inplay first.
    if str(move.pred) in PLAY_PREDS:
        def monastery_trash(move, i, bL, moves, cS):
            moveCoppers = move.items['COPPER']
            inPlayCoppers = cS[('INPLAYS', move.player)]['COPPER']
            coppersToKill = min(moveCoppers, inPlayCoppers)

            if coppersToKill > 0:
                copperStack = Cardstack({'COPPER': coppersToKill})
                itemsSansCoppers = move.items - copperStack

                cS.move(move.player, 'HANDS', 'TRASH', itemsSansCoppers)
                cS.move(move.player, 'INPLAYS', 'TRASH', copperStack)
            else:
                transfer('HANDS', 'TRASH', move, cS)

        return {exc: bL for exc in [Exception(check(['TRASH'], ['COPPER']),
                                              monastery_trash),
                                    exc_standardTrash]}


Cards['MONASTERY'].action = monastery_action


def necromancer_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        playExc = checkMove(['PLAY'], 'TRASH', 'TRASH')
        onPlayExc = Exception(check(['PLAY']), standardOnPlay)
        return {exc: bL for exc in [playExc, onPlayExc]}


Cards['NECROMANCER'].action = necromancer_action

Cards['NIGHT WATCHMAN'].action = decksifter


def pixie_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        for scan in moves[i + 1: i + bL]:
            if str(scan.pred) == 'TAKES BOONHEX':
                whichBoon = scan.items.primary()
                break

        if whichBoon == 'The Flame\'s Gift':
            pixieStack = Cardstack({"PIXIE": 1})
            otherThings = move.items - pixieStack

            def pixieTrash(pixieStack, otherThings):
                def out_function(move, i, bL, moves, cS):
                    cS.move(move.player, 'INPLAYS', 'TRASH', pixieStack)
                    cS.move(move.player, 'HANDS', 'TRASH', otherThings)
                return out_function

            pixieTrashExc = Exception(check(['TRASH'], ['Pixie']),
                                      pixieTrash(pixieStack, otherThings))
            pixieOnTrashExc = Exception(check(['TRASH'], ['Pixie']),
                                        standardOnTrash)
            return {exc: bL for exc in [pixieTrashExc, pixieOnTrashExc]}
        else:
            t = {checkMove(['TRASH'], 'INPLAYS', 'TRASH'): bL}

            if whichBoon == 'The Sun\'s Gift':
                t[exc_revealTopdeck] = bL
                t[exc_revealDiscard] = bL

            elif whichBoon == 'The Moon\'s Gift':
                t[exc_harbinger] = bL
            return t


Cards['PIXIE'].action = pixie_action

Cards['TRAGIC HERO'].action = selftrasher


def vampire_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        t = {checkMove(['RETURN'], 'INPLAYS', 'SUPPLY', ['VAMPIRE']): bL}
        t.append(standard_boonhex(cM, gS, exc, tExc, pers))
        return t


Cards['VAMPIRE'].action = vampire_action

Cards['MAGIC LAMP'].action = selftrasher


def pasture_worth(gameState, player):
    playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
    return playerDeck['ESTATE']


Cards['PASTURE'].worth = pasture_worth


def bats_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        return {checkMove(['RETURN'], 'INPLAYS', 'SUPPLY', ['BAT']): bL}


Cards['BAT'].action = bats_action


def ghost_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        setExc = checkMove(['SET ASIDE'], 'DECKS', 'OTHERS')
        return {exc: bL for exc in [exc_revealDiscard, setExc]}


Cards['GHOST'].action = ghost_action

Cards["WILL-O'-WISP"].action = decksifter


def wish_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        gainExc = checkMove(['GAIN'], 'SUPPLY', 'HANDS')
        onGainExc = Exception(check(['GAIN']), onGains('HANDS'))
        return {exc: bL for exc in [gainExc, onGainExc]}


Cards['WISH'].action = wish_action


def zombiemason_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        trashExc = checkMove(['TRASH'], 'DECKS', 'TRASH')
        return {exc: bL for exc in [trashExc, exc_standardTrash]}


Cards['ZOMBIE MASON'].action = zombiemason_action

Cards['ZOMBIE SPY'].action = decksifter

Cards['ENVOY'].action = deckchuck


def prince_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        return{checkMove(['SET ASIDE'], 'HANDS', 'OTHERS'): bL}


Cards['PRINCE'].action = prince_action


def summon_action(move, i, bL, moves, cS):
    if str(move.pred) == 'BUY':
        return{checkMove(['SET ASIDE'], 'SUPPLY', 'OTHERS'): bL}


Cards['SUMMON'].action = summon_action

# -- PREDS -- #


def newTurnAction(move, i, bL, moves, cS):
    cS['ACTIVE_PLAYER'] = move.player
    cS['PHASE'] = 0
    return {}


Preds['NEW TURN'].action = newTurnAction


def standardGains(source, destination='DISCARDS'):
    def out_function(move, i, bL, moves, cS):
        targetStuff = deepcopy(move.items)
        t = {}
        for card in move.items:
            if card == 'NOMAD CAMP':
                exceptionalStuff = Cardstack({card: targetStuff[card]})
                targetStuff -= exceptionalStuff

                cS.move(move.player, source, 'DECKS', exceptionalStuff)
                t.update(onGains('DECKS')(move, i, bL, moves, cS))

            if card in ['DEN OF SIN',
                        'GUARDIAN',
                        'GHOST TOWN',
                        'NIGHT WATCHMAN']:
                exceptionalStuff = Cardstack({card: targetStuff[card]})
                targetStuff -= exceptionalStuff

                cS.move(move.player, source, 'HANDS', exceptionalStuff)
                t.update(onGains('HANDS')(move, i, bL, moves, cS))

        if len(targetStuff) > 0:
            for card in targetStuff:
                cardStuff = Cardstack({card: targetStuff[card]})
                cS.move(move.player, source, destination, cardStuff)
                t.update(onGains(destination)(move, i, bL, moves, cS))

        return t
    return out_function


def buyAndGainAction(move, i, bL, moves, cS):
    standardGains('SUPPLY')(move, i, bL, moves, cS)
    cS['PHASE'] = 1
    return {}


Preds['BUY AND GAIN'].action = buyAndGainAction

Preds['GAIN TOPDECK'].action = standardGains('SUPPLY', 'DECKS')

Preds['GAIN TRASH'].action = standardGains('TRASH')

Preds['GAIN'].action = standardGains('SUPPLY')


def trashAction(move, i, bL, moves, cS):
    cS.move(move.player, 'HANDS', 'TRASH', move.items)

    return {checkMove(['DISCARD'], 'HANDS', 'DISCARDS',
                      ['MARKET SQURE']): bL}


Preds['TRASH'].action = trashAction

Preds['DISCARD'].action = moveFunct('HANDS', 'DISCARDS')

Preds['PLAY'].action = moveFunct('HANDS', 'INPLAYS')


def topdeckAction(move, i, bL, moves, cS):
    if move.indent == 0:
        # Probably Scheme (or walled village / alch / treasury)
        cS.move(move.player, 'INPLAYS', 'DECKS', move.items)

    else:
        cS.move(move.player, 'HANDS', 'DECKS', move.items)


Preds['TOPDECK'].action = topdeckAction

for p in ['WHARF DRAW', 'HIRELING DRAW', 'WOODS DRAW', 'ENCHANTRESS DRAW',
          'CARAVAN DRAW', 'TACTICIAN DRAW', 'DRAW FROM', 'GT DRAW']:
    Preds[p].action = moveFunct('DECKS', 'HANDS')


def drawAction(move, i, bL, moves, cS):
    activePlayer = cS['ACTIVE_PLAYER']
    # Cleanup
    if move.isCleanup:
        if move.player == activePlayer:
            cS.move(move.player, 'INPLAYS', 'DISCARDS',
                    cS[('INPLAYS', move.player)])
            cS.move(move.player, 'HANDS', 'DISCARDS',
                    cS[('HANDS', move.player)])

    cS.move(move.player, 'DECKS', 'HANDS', move.items)
    return {}


Preds['DRAW'].action = drawAction


def inhandAction(move, i, bL, moves, cS):
    if move.indent == 0 and move.items.primary() == 'FAITHFUL HOUND':
        cS.move(move.player, 'OTHERS', 'HANDS', move.items)
    else:
        # Villa's handled somewhere else
        if move.items.primary() != 'VILLA':
            cS.move(move.player, 'DECKS', 'HANDS', move.items)
    return {}


Preds['PUT INHAND'].action = inhandAction


def setAsideAction(move, i, bL, moves, cS):
    if move.items.primary() not in BOONHEX:
        cS.move(move.player, 'INPLAYS', 'OTHERS', move.items)
    return {}


Preds['SET ASIDE'].action = setAsideAction

Preds['PUT ONTO'].action = moveFunct('HANDS', 'OTHERS')

Preds['CALL'].action = moveFunct('OTHERS', 'INPLAYS')


def deckDiscardAction(move, i, bL, moves, cS):
    cS.move(move.player, 'DECKS', 'DISCARDS', cS[('DECKS', move.player)])
    return {}


Preds['DISCARD DECK'].action = deckDiscardAction

Preds['SHUFFLE INTO'].action = moveFunct('DISCARDS', 'DECKS')

Preds['RETURN TO'].action = moveFunct('INPLAYS', 'SUPPLY')

Preds['RETURN'].action = moveFunct('HANDS', 'SUPPLY')

Preds['RECEIVE.'].action = moveFunct('SUPPLY', 'DISCARDS')


# 37
def standard_boonhex(move, i, bL, moves, cS):
    whichBoon = move.items.primary()
    for l in range(1, len(moves) - i):
        if move[i + l].items.primary() == whichBoon and\
           str(move[i + l].pred) == 'DISCARD':
            break

    if whichBoon == 'The Sun\'s Gift':
        return {exc: l for exc in [exc_revealTopdeck, exc_revealDiscard]}

    elif whichBoon == 'The Moon\'s Gift':
        return {exc_harbinger: l}

    elif whichBoon == 'Locusts':
        return {exc_revealTrash: l}

    elif whichBoon == 'War':
        return {exc: l for exc in [exc_revealTrash, exc_revealDiscard]}

    elif whichBoon == 'Greed':
        greed_gain = checkMove(['GAIN'], 'SUPPLY', 'DECKS', ['COPPER'])
        greed_ongain = Exception(check(['GAIN'], ['COPPER']),
                                 onGains('DECKS', Cardstack({'COPPER': 1})))
        return {exc: l for exc in [greed_gain, greed_ongain]}

    elif whichBoon == 'Plague':
        plague_gain = checkMove(['GAIN'], 'SUPPLY', 'HANDS', ['CURSE'])
        plague_ongain = Exception(check(['GAIN'], ['CURSE']),
                                  onGains('DECKS', Cardstack({'CURSE': 1})))
        return {exc: l for exc in [plague_gain, plague_ongain]}

    elif whichBoon == 'Bad Omens':
        return {exc: l for exc in [exc_harbinger, exc_revealDiscard]}

    elif whichBoon == 'Famine':
        famine_discard = checkMove(['SHUFFLE INTO'], 'DECKS', 'DECKS')
        return {exc: l for exc in [famine_discard, exc_revealDiscard]}


Preds['RECEIVE BOONHEX'].action = standard_boonhex


def passAction(move, i, bL, moves, cS):
    cS[('HANDS', move.player)] -= move.items
    cS[('HANDS', 1 - move.player)] += move.items


Preds['PASS'].action = passAction

Preds['STARTS'].action = moveFunct('SUPPLY', 'DECKS')


def buyAction(move, i, bL, moves, cS):
    cS.phase = 1


Preds['BUY'].action = buyAction


def shuffleAction(move, i, bL, moves, cS):
    activePlayer = move.player
    # Cleanup
    if move.isCleanup:
        cS.move(activePlayer, 'INPLAYS', 'DISCARDS',
                cS[('INPLAYS', activePlayer)])
        cS.move(activePlayer, 'HANDS', 'DISCARDS', cS[('HANDS', activePlayer)])

    cS.move(activePlayer, 'DISCARDS', 'DECKS', cS[('DISCARDS', activePlayer)])
    return {}


Preds['SHUFFLE'].action = shuffleAction


def wishAction(move, i, bL, moves, cS):
    cS.move(move.player, 'DECKS', 'HANDS',
            Cardstack({move.items.primary(): 1}))


Preds['WISH SUCCESS'].action = wishAction


for p in ['DRAW GEAR', 'DRAW HAVEN', 'DRAW ARCHIVE', 'CRYPT']:
    Preds[p].action = moveFunct('OTHERS', 'HANDS')


def turnStartAction(move, i, bL, moves, cS):
    t = {exc: bL for exc in [checkMove(['PLAY'], 'OTHERS', 'INPLAYS'),
                             Exception(check(['PLAY']), onPlay),
                             checkMove(['PUT INHAND'], 'OTHERS', 'HANDS',
                                       ['HORSE TRADERS'])]}

    # Probably Cobbler
    def gainNow(cM):
        # Amulet!
        isSilver = move.items.primary() == 'Silver'
        return str(move.pred) == 'GAIN' and move.indent == 1 and not isSilver

    def add_stuff(move, i, bL, moves, cS):
        thisBoon = move.items.primary()
        for l in range(len(moves) - i):
            if move.items.primary() == thisBoon and\
               str(move.pred) == 'DISCARD':
                break

        exc_gainNormally = Exception(check(['GAIN']),
                                     moveException('SUPPLY', 'DISCARDS'),
                                     priority=1)
        exc_onGainNormally = Exception(check(['GAIN']),
                                       onGains('DISCARDS'),
                                       priority=1)

        return {exc: l for exc in [exc_gainNormally, exc_onGainNormally]}

    t.update({Exception(check(['RECEIVES BOONHEX']), add_stuff): bL})

    t.update({exc: bL for exc in [Exception(gainNow, moveException('SUPPLY',
                                                                   'HANDS')),
                                  Exception(gainNow, onGains('DECKS'))]})

    return t


Preds['TURN START'].action = turnStartAction


def genericVP(move, i, bL, moves, cS):
    cS['VPS'][move.player] += int(move.items['ARGUMENT'].split('/')[0])
    return {}


for p in ['SHIELD GAIN', 'SHIELD GET', 'SHIELD GROUNDSKEEPER', 'SHIELD GOONS',
          'SHIELD OTHER']:
    Preds[p].action = genericVP


def obelisk_choice(move, i, bL, moves, cS):
    target = move.items.primary()
    cS['OBELISK'] = [target]
    for pair in PAIRS:
        if target in pair:
            cS['OBELISK'] = pair
            return {}


Preds['OBELISK CHOICE'].action = obelisk_choice

Preds['SET ASIDE WITH'].action = moveFunct('HANDS', 'OTHERS')


def inheritAction(move, i, bL, moves, cS):
    cS.move(move.player, 'SUPPLY', 'OTHERS', move.items)
    cS['INHERITED_CARDS'][move.player] = move.items.cardList()[0]
    return {}


Preds['INHERIT'].action = inheritAction


def predDonateAction(move, i, bL, moves, cS):
    def moveEverything(move, i, bL, moves, cS):
        cS.move(move.player, 'DECKS', 'HANDS',
                cS[('DECKS', move.player)])
        cS.move(move.player, 'DISCARDS', 'HANDS',
                cS[('DISCARDS', move.player)])

    def shuffleBack(move, i, bL, moves, cS):
        cS.move(move.player, 'HANDS', 'DECKS',
                cS[('HANDS', move.player)])

    putExc = Exception(check(['PUT INHAND']), moveEverything)
    shuffleExc = Exception(check(['SHUFFLE INTO']), shuffleBack)
    return {exc: bL for exc in [putExc, shuffleExc]}


Preds['BETWEEN TURNS'].action = predDonateAction


def urchinTrash(move, i, bL, moves, cS):
    indentCap = move.indent
    for scan in moves[i + 1:]:
        if scan.indent < indentCap or \
                str(scan.pred) == 'NEW TURN':
            break
        else:
            if str(scan.pred) == 'GAIN' and \
                    scan.items.primary() == 'MERCENARY':
                cS.move(move.player, 'INPLAYS', 'TRASH', move.items)
                return {}

    cS.move(move.player, 'HANDS', 'TRASH', move.items)
    return {}


def hermitTrash(move, i, bL, moves, cS):
    indentCap = move.indent
    for scan in moves[i + 1:]:
        if scan.indent < indentCap or \
                str(scan.pred) == 'NEW TURN':
            break
        else:
            if str(scan.pred) == 'GAIN' and \
                    scan.items.primary() == 'MADMAN':
                cS.move(move.player, 'INPLAYS', 'TRASH', move.items)
                return {}

    cS.move(move.player, 'HANDS', 'TRASH', move.items)
    return {}


urchinPers = Exception(check(['TRASH'], ['HERMIT']), urchinTrash)
hermitPers = Exception(check(['TRASH'], ['HERMIT']), hermitTrash)
encampmentPers = checkMove(['RETURN TO'], 'OTHERS', 'SUPPLY', ['ENCAMPMENT'])
travellerPers = checkMove(['RETURN'], 'INPLAYS', 'SUPPLY', TRAVELLERS)
WMPers = checkMove(['DISCARD'], 'OTHERS', 'DISCARDS', ['WINE MERCHANT'])
returnStates = Exception(check(['RETURN'], ['MISERABLE',
                                            'ENVIOUS',
                                            'DELUDED',
                                            'LOST IN THE WOODS']), empty)

persistents = [urchinPers, hermitPers, encampmentPers, travellerPers,
               WMPers, returnStates]
for exc in persistents:
    exc.persistent = True
INTRINSIC_EXCEPTIONS = {exc: -1 for exc in persistents}
