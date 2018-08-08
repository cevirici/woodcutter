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


class Card:
    def __init__(self, index, simple_name, multi_name, phrase_name,
                 cost, supply_type, border_color, card_color,
                 action, worth=lambda x, y: 0):

        self.index = index
        self.simple_name = simple_name
        self.multi_name = multi_name
        self.phrase_name = phrase_name
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
        return self.index == other.index

    def names(self):
        return [self.simple_name, self.multi_name, self.phrase_name]


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

cardFile = open(os.path.join(settings.STATIC_ROOT,
                             'woodcutter/data/carddata.txt'), 'r')
for i, line in enumerate(cardFile):
    t = line.split(',')
    c = Card(i, t[1], t[2], t[3], t[4],
             t[5], t[6], t[7], empty)
    if len(t) > 8:
        c.worth = staticWorth(int(t[8]))

    Cards[t[1].upper()] = c
    CardList.append(c)

cardFile.close()

predFile = open(os.path.join(settings.STATIC_ROOT,
                             'woodcutter/data/preddata.txt'), 'r')
for i, line in enumerate(predFile):
    t = line.split(',')
    p = Pred(i, t[1], empty, t[2])
    Preds[t[2]] = p
    PredList.append(p)

predFile.close()

predParseOrder = PredList[:26] + PredList[119:119] + PredList[26:]

PLAY_PREDS = ('PLAY', 'PLAY AGAIN', 'PLAY THIRD')
GAIN_PREDS = ('GAIN', 'BUY AND GAIN', 'GAIN TOPDECK', 'GAIN TRASH')


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
    if move.items.count() > 0:
        cS.move(move.player, src, dest, move.items)
    return {}


def moveFunct(src, dest):
    def out_function(move, i, bL, moves, cS):
        transfer(src, dest, move, cS)
    return out_function


def checkMove(predList, src, dest, targetList=[]):
    return Exception(check(predList, targetList),
                     moveFunct(src, dest))


def gainCash(amount):
    def out_function(move, i, bL, moves, cS):
        cS['COINS'][move.player] += amount
        return {}

    return out_function


def onGains(src, gainedCards):
    def wasGained(predList):
        def out_function(move):
            if str(move.pred) not in predList:
                return False
            return gainedCards > move.items
        return out_function

    def villaExcAction(move, i, bL, moves, cS):
        transfer(src, 'HANDS', moves, cS)
        cS.phase = 0

    villaException = Exception(check(['PUT INHAND'], ['VILLA']),
                               villExcAction)

    def out_function(move, i, bL, moves, cS):
        newExcs = {}

        if 'VILLA' in gainedCards:
            newExcs[villaException] = bL

        for exc in [Exception(wasGained(['TOPDECK']), moveFunct(src, 'DECKS')),
                    Exception(wasGained(['TRASH']), moveFunct(src, 'TRASH')),
                    Exception(wasGained(['RETURN']), moveFunct(src, 'SUPPLY'))
                    ]:
            newExcs[exc] = bL
        return newExcs

    return out_function


def onPlay(move, i, bL, moves, cS):
    for card in move.items.strip():
        for i in range(move.items[card]):
            Cards[card].action(move, i, bL, moves, cS)


def onTrash(move, i, bL, moves, cS):
    for card in move.items.strip():
        for i in range(move.items[card]):
            Cards[card].action(move, i, bL, moves, cS)


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
        onGainExc = Exception(check(['GAIN']), onGains('DECKS', move.items))
        return {exc: bL for exc in [gainExc, onGainExc]}


def emulate(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        playExc = checkMove(['PLAY'], 'SUPPLY', 'SUPPLY')
        onPlayExc = Exception(check(['PLAY']), standardOnPlay)
        return {exc: bL for exc in [playExc, onPlayExc]}


# -- Individual Cards -- #

def estate_action(move, i, bL, moves, cS):
    return cS['INHERITED_CARDS'][move.player].action(move, i, bL, moves, cS)


Cards['ESTATE'].action = estate_action


def artisan_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        onGainExc = Exception(check(['GAIN']), onGains('HANDS', move.items))
        return {exc_gainHand: bL, onGainExc: bL}


Cards['ARTISAN'].action = artisan_action

Cards['BANDIT'].action = banditlike


def bureaucrat_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        onGainExc = Exception(check(['GAIN']), onGains('DECKS', move.items))
        gainExc = checkMove(['GAIN'], 'SUPPLY', 'DECKS', ['Silver'])
        return {exc: bL for exc in [onGainExc, gainExc]}


Cards['BUREAUCRAT'].action = bureaucrat_action


def gardens_worth(gS, player):
    return gS.crunch(PERSONAL_ZONES, (player)).count() // 10


Cards['GARDENS'].worth = gardens_worth


def harbinger_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        return {exc_harbinger: bL}


Cards['HARBINGER'].action = harbinger_action


def library_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        setAsideExc = checkMove(['SETS ASIDE WITH'], 'DECKS', 'OTHERS')
        libDiscardExc = checkMove(['DISCARD'], 'OTHERS', 'DISCARDS')
        return {exc: bL for exc in [setAsideExc, libDiscardExc]}


Cards['LIBRARY'].action = library_action


def mine_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        onGainExc = Exception(check(['GAIN']), onGains('HANDS', move.items))
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
                                              onGains('DISCARDS', move.items))
                                    ]}


Cards['LURKER'].action = lurker_action

Cards['MINING VILLAGE'].action = selftrasher


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
                              onGains('HANDS', move.items))
        return {exc: bL for exc in [gainExc, onGainExc]}


Cards['TORTURER'].action = torturer_action


def tradepost_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        onGainExc = Exception(check(['GAIN'], ['Silver']),
                              onGains('HANDS', move.items))
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
                              onGains('HANDS', move.items))
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

Cards['PIRATE SHIP'] = banditlike


def seahag_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        gainExc = checkMove(['GAIN'], 'SUPPLY', 'DECKS', ['CURSE'])
        onGainExc = Exception(check(['GAIN'], ['CURSE']),
                              onGains('DECKS', move.items))
        return {exc: bL for exc in [exc_revealDiscard, gainExc, onGainExc]}


Cards['SEA HAG'].action = seahag_act


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


Cards['VINEYARDS'].worth = vineyard_worth


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
                              onGains('DECKS', move.items))
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
        onGainExc = Exception(check(['GAIN']), onGains('DECKS', move.items))
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
                              onGains('DECKS', move.items))
        return {exc: bL for exc in [gainExc, onGainExc]}


Cards["FOOL'S GOLD"].action = fg_action


def igg_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        gainExc = checkMove(['GAIN'], 'SUPPLY', 'HANDS', ['COPPER'])
        onGainExc = Exception(check(['GAIN'], ['COPPER']),
                              onGains('HANDS', move.items))
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
                              onGains('HANDS', move.items))
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


def annaTrash(knightPlayer):
    def out_function(move):
        trashPart = str(move.pred) == 'TRASH' and \
            move.items.primary() != 'DAME ANNA'
        return trashPart and move.player == knightPlayer
    return out_function


def annaAction(move, i, bL, moves, cS):
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


for knight in KNIGHTS:
    if knight == 'DAME ANNA':
        Cards[knight].action = annaAction
    else:
        Cards[knight].action = knightAction


def deathcart_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        trashExc = checkMove(['TRASH'], 'INPLAYS', 'TRASH', ['Death Cart'])
        onTrashExc = Exception(check(['TRASH'], ['Death Cart']), standardOnTrash)
        return {exc: bL for exc in [trashExc, onTrashExc]}


t = Card('Death Cart', 'Death Carts', 'a Death Cart', 4, 0, 'c4c0b4', '826636', deathcart_action)
standardCards.append(t)


# 190: Feodum
def feodum_worth(gameState, player):
    playerDeck = gameState.crunch(['DECKS', 'DISCARDS', 'HANDS',
                                   'OTHERS', 'INPLAYS'], (player))

    for card in playerDeck:
        if standardCards[card].simple_name == 'Silver':
            return playerDeck[card] // 3

    return 0


t = Card('Feodum', 'Feoda', 'a Feodum', 4, 0, '9cbe8a', 'b4a67e', empty, feodum_worth)
standardCards.append(t)

# 191: Forager
t = Card('Forager', 'Foragers', 'a Forager', 3, 0, 'c4c0b4', 'a46618', empty)
standardCards.append(t)


# 192: Fortress
def fortress_action(move, i, bL, moves, cS):
    if str(move.pred) in ['TRASH']:
        exc.append(checkMove(['PUT INHAND'], 'TRASH', 'HANDS'))


t = Card('Fortress', 'Fortresses', 'a Fortress', 4, 0, 'c4c0b4', '62524c', fortress_action)
standardCards.append(t)


# 193: Graverobber
def graverobber_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        isRemodelling = False
        for chunk in cM[1:]:
            if chunk[0].predName() == 'TRASH':
                isRemodelling = True

        if not isRemodelling:
            exc.append(checkMove(['GAIN'], 'TRASH', 'DECKS'))


t = Card('Graverobber', 'Graverobbers', 'a Graverobber', 5, 0, 'c4c0b4', '4e4052', graverobber_action)
standardCards.append(t)


# 194: Hermit
def hermit_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        playerDiscard = gS[-1].DISCARDS[cM[0].player]

        def hermitTrashCondition(playerDiscard):
            def out_function(cM):
                return (cM[0].items - playerDiscard).count() == 0 and str(move.pred) == 'TRASH'
            return out_function

        exc.append(Exception(hermitTrashCondition(playerDiscard),
                             moveException('DISCARDS', 'TRASH')))


t = Card('Hermit', 'Hermits', 'a Hermit', 3, 0, 'c4c0b4', '977d5b', hermit_action)
standardCards.append(t)

# 195: Hovel
t = Card('Hovel', 'Hovels', 'a Hovel', 1, 2, 'a48892', '25716f', empty)
standardCards.append(t)

# 196: Hunting Grounds
t = Card('Hunting Grounds', 'Hunting Grounds', 'a Hunting Grounds', 6, 0, 'c4c0b4', 'a08250', empty)
standardCards.append(t)


# 197: Ironmonger
def ironmonger_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(exc_revealDiscard)
        exc.append(exc_revealTopdeck)


t = Card('Ironmonger', 'Ironmongers', 'an Ironmonger', 4, 0, 'c4c0b4', '72787a', ironmonger_action)
standardCards.append(t)

# 198: Junk Dealer
t = Card('Junk Dealer', 'Junk Dealers', 'a Junk Dealer', 5, 0, 'c4c0b4', '7b5f2d', empty)
standardCards.append(t)

# 199: Madman
t = Card('Madman', 'Madmen', 'a Madman', 0, 1, 'c4c0b4', '8b513d', empty)
standardCards.append(t)

# 200: Market Square
t = Card('Market Square', 'Market Squares', 'a Market Square', 3, 0, '8ca2be', '956d43', empty)
standardCards.append(t)

# 201: Marauder
t = Card('Marauder', 'Marauders', 'a Marauder', 4, 0, 'c4c0b4', '7e4826', empty)
standardCards.append(t)

# 202: Mercenary
t = Card('Mercenary', 'Mercenaries', 'a Mercenary', 0, 1, 'c4c0b4', '6b8193', empty)
standardCards.append(t)

# 203: Mystic
t = Card('Mystic', 'Mystics', 'a Mystic', 5, 0, 'c4c0b4', '695729', empty)
standardCards.append(t)

# 204: Necropolis
t = Card('Necropolis', 'Necropolis', 'a Necropolis', 1, 2, 'd59f89', '778793', empty)
standardCards.append(t)

# 205: Overgrown Estate
t = Card('Overgrown Estate', 'Overgrown Estates', 'an Overgrown Estate', 1, 2, 'b4a65e', '58664c', empty)
standardCards.append(t)


# 206: Pillage
def pillage_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(checkMove(['TRASH'], 'INPLAYS', 'TRASH',
                                     ['Pillage']))


t = Card('Pillage', 'Pillages', 'a Pillage', 5, 0, 'c4c0b4', '8d7f63', pillage_action)
standardCards.append(t)

# 207: Poor House
t = Card('Poor House', 'Poor Houses', 'a Poor House', 1, 0, 'c4c0b4', '65573d', empty)
standardCards.append(t)


# 208: Procession
def procession_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(exc_inplayTrash)
        exc.append(exc_standardTrash)


t = Card('Procession', 'Processions', 'a Procession', 4, 0, 'c4c0b4', '775f3d', procession_action)
standardCards.append(t)

# 209: Rats
t = Card('Rats', 'Rats', 'a Rats', 4, 0, 'c4c0b4', '795743', empty)
standardCards.append(t)


# 210: Rebuild
def rebuild_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(exc_revealTrash)
        exc.append(exc_revealDiscard)


t = Card('Rebuild', 'Rebuilds', 'a Rebuild', 5, 0, 'c4c0b4', '64748c', rebuild_action)
standardCards.append(t)


# 211: Rogue
def rogue_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(checkMove(['GAIN'], 'TRASH', 'DISCARDS'))
        exc.append(Exception(check(['GAIN']),
                             standardOnGains('DISCARDS')))
        exc.append(exc_revealDiscard)
        exc.append(exc_revealTrash)


t = Card('Rogue', 'Rogues', 'a Rogue', 5, 0, 'c4c0b4', '363c4c', rogue_action)
standardCards.append(t)

# 212: Ruined Library
t = Card('Ruined Library', 'Ruined Libraries', 'a Ruined Library', 0, -1, 'b29462', '806a34', empty)
standardCards.append(t)

# 213: Ruined Market
t = Card('Ruined Market', 'Ruined Markets', 'a Ruined Market', 0, -1, 'b29462', '6d5753', empty)
standardCards.append(t)

# 214: Ruined Village
t = Card('Ruined Village', 'Ruined Villages', 'a Ruined Village', 0, -1, 'b29462', 'a4886a', empty)
standardCards.append(t)


# 215: Sage
def sage_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(exc_revealDiscard)


t = Card('Sage', 'Sages', 'a Sage', 3, 0, 'c4c0b4', '89612f', sage_action)
standardCards.append(t)


# 216: Scavenger
def scavenger_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(exc_harbinger)


t = Card('Scavenger', 'Scavengers', 'a Scavenger', 4, 0, 'c4c0b4', '34404e', scavenger_action)
standardCards.append(t)

# 217: Sir Bailey
t = Card('Sir Bailey', 'Sir Baileys', 'a Sir Bailey', 5, -1, 'c4c0b4', '506070', standardKnightsAction)
standardCards.append(t)

# 218: Sir Destry
t = Card('Sir Destry', 'Sir Destries', 'a Sir Destry', 5, -1, 'c4c0b4', '797d7f', standardKnightsAction)
standardCards.append(t)

# 219: Sir Martin
t = Card('Sir Martin', 'Sir Martins', 'a Sir Martin', 4, -1, 'c4c0b4', 'cc9e60', standardKnightsAction)
standardCards.append(t)

# 220: Sir Michael
def michael_action(move, i, bL, moves, cS):
    def michaelRevealException(outerExceptions):
        def out_function(move, i, bL, moves, cS):
            outerExceptions.append(exc_revealDiscard)
        return out_function

    if str(move.pred) in PLAY_PREDS:
        exc.append(Exception(knightsTrashCondition(cM[0].player),
                             moveException('DECKS', 'TRASH')))
        exc.append(exc_standardTrash)
        exc.append(Exception(check(['REVEAL']),
                             michaelRevealException(exc)))
        exc.append(Exception(knightsSuicideCondition(cM[0].player),
                             moveException('INPLAYS', 'TRASH')))


t = Card('Sir Michael', 'Sir Michaels', 'a Sir Michael', 5, -1, 'c4c0b4', '47454b', michael_action)
standardCards.append(t)

# 221: Sir Vander
t = Card('Sir Vander', 'Sir Vanders', 'a Sir Vander', 5, -1, 'c4c0b4', '9ca6ac', standardKnightsAction)
standardCards.append(t)

# 222: Spoils
t = Card('Spoils', 'Spoils', 'a Spoils', 0, 1, 'd8c280', '646032', empty)
standardCards.append(t)

# 223: Storeroom
t = Card('Storeroom', 'Storerooms', 'a Storeroom', 3, 0, 'c4c0b4', '69492f', empty)
standardCards.append(t)

# 224: Squire
t = Card('Squire', 'Squires', 'a Squire', 2, 0, 'c4c0b4', '937b4b', empty)
standardCards.append(t)


# 225: Survivors
def survivors_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(exc_revealTopdeck)
        exc.append(exc_revealDiscard)


t = Card('Survivors', 'Survivors', 'a Survivors', 0, -1, 'b29462', '706a46', survivors_action)
standardCards.append(t)

# 226: Urchin
t = Card('Urchin', 'Urchins', 'an Urchin', 3, 0, 'c4c0b4', '634b33', empty)
standardCards.append(t)


# 227: Vagrant
def vagrant_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(exc_revealTopdeck)


t = Card('Vagrant', 'Vagrants', 'a Vagrant', 2, 0, 'c4c0b4', '593f2b', vagrant_action)
standardCards.append(t)


# 228: Wandering Minstrel
def minstrel_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(exc_revealTopdeck)
        exc.append(exc_revealDiscard)


t = Card('Wandering Minstrel', 'Wandering Minstrels', 'a Wandering Minstrel', 4, 0, 'c4c0b4', '905414', minstrel_action)
standardCards.append(t)


# 229: Advisor
def advisor_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(exc_revealDiscard)


t = Card('Advisor', 'Advisors', 'an Advisor', 4, 0, 'c4c0b4', '77675b', advisor_action)
standardCards.append(t)

# 230: Baker
t = Card('Baker', 'Bakers', 'a Baker', 5, 0, 'c4c0b4', '815b3b', empty)
standardCards.append(t)

# 231: Butcher
t = Card('Butcher', 'Butchers', 'a Butcher', 5, 0, 'c4c0b4', '9c6426', empty)
standardCards.append(t)

# 232: Candlestick Maker
t = Card('Candlestick Maker', 'Candlestick Makers', 'a Candlestick Maker', 2, 0, 'c4c0b4', '7d6137', empty)
standardCards.append(t)


# 233: Doctor
def doctor_action(move, i, bL, moves, cS):
    if str(move.pred) in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD', 'BUY']:
        exc.append(exc_revealTopdeck)
        exc.append(exc_revealDiscard)
        exc.append(exc_revealTrash)
        exc.append(exc_standardTrash)


t = Card('Doctor', 'Doctors', 'a Doctor', 3, 0, 'c4c0b4', '895923', doctor_action)
standardCards.append(t)


# 234: Herald
def herald_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(checkMove(['PLAY'], 'DECKS', 'INPLAYS'))
        exc.append(Exception(check(['PLAY']), standardOnPlay))

    if str(move.pred) in ['BUY']:
        exc.append(exc_harbinger)


t = Card('Herald', 'Heralds', 'a Herald', 4, 0, 'c4c0b4', '996941', herald_action)
standardCards.append(t)


# 235: Journeyman
def journeyman_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(exc_revealDiscard)


t = Card('Journeyman', 'Journeymen', 'a Journeyman', 5, 0, 'c4c0b4', '78704e', journeyman_action)
standardCards.append(t)

# 236: Masterpiece
t = Card('Masterpiece', 'Masterpieces', 'a Masterpiece', 3, 0, 'd8c280', 'd5c361', empty)
standardCards.append(t)

# 237: Merchant Guild
t = Card('Merchant Guild', 'Merchant Guilds', 'a Merchant Guild', 5, 0, 'c4c0b4', 'a44410', empty)
standardCards.append(t)

# 238: Plaza
t = Card('Plaza', 'Plazas', 'a Plaza', 4, 0, 'c4c0b4', '87573f', empty)
standardCards.append(t)


# 239: Taxman
def taxman_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(checkMove(['GAIN'], 'SUPPLY', 'DECKS'))
        exc.append(Exception(check(['GAIN']),
                             standardOnGains('DECKS')))


t = Card('Taxman', 'Taxmen', 'a Taxman', 4, 0, 'c4c0b4', '70583a', taxman_action)
standardCards.append(t)

# 240: Soothsayer
t = Card('Soothsayer', 'Soothsayers', 'a Soothsayer', 5, 0, 'c4c0b4', '514135', empty)
standardCards.append(t)

# 241: Stonemason
t = Card('Stonemason', 'Stonemasons', 'a Stonemason', 2, 0, 'c4c0b4', '915d23', empty)
standardCards.append(t)

# 242: Alms
t = Card('Alms', 'Alms', 'an Alms', 0, 2, 'a9a39d', '9f793f', empty)
standardCards.append(t)

# 243: Amulet
t = Card('Amulet', 'Amulets', 'an Amulet', 3, 0, 'dda561', 'd39d25', empty)
standardCards.append(t)


# 244: Artificer
def artificer_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(checkMove(['GAIN'], 'SUPPLY', 'DECKS'))
        exc.append(Exception(check(['GAIN']),
                             standardOnGains('DECKS')))


t = Card('Artificer', 'Artificers', 'an Artificer', 5, 0, 'c4c0b4', '754f2b', artificer_action)
standardCards.append(t)

# 245: Ball
t = Card('Ball', 'Balls', 'a Ball', 5, 2, 'a9a39d', '8b6323', empty)
standardCards.append(t)


# 246: Bonfire
def bonfire_action(move, i, bL, moves, cS):
    if str(move.pred) in ['BUY']:
        exc.append(exc_inplayTrash)
        exc.append(exc_standardTrash)


t = Card('Bonfire', 'Bonfires', 'a Bonfire', 3, 2, 'a9a39d', '844e52', bonfire_action)
standardCards.append(t)

# 247: Borrow
t = Card('Borrow', 'Borrows', 'a Borrow', 0, 2, 'a9a39d', '8a3620', empty)
standardCards.append(t)

# 248: Bridge Troll
t = Card('Bridge Troll', 'Bridge Trolls', 'a Bridge Troll', 5, 0, 'dda561', '524830', empty)
standardCards.append(t)

# 249: Caravan Guard
t = Card('Caravan Guard', 'Caravan Guards', 'a Caravan Guard', 3, 0, 'a7a39b', '7c8e68', empty)
standardCards.append(t)

# 250: Champion
t = Card('Champion', 'Champions', 'a Champion', 6, 1, 'dda561', '594c3e', empty)
standardCards.append(t)


# 251: Coin of the Realm
def standard_reserve(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(checkMove(['PUT ONTO'], 'INPLAYS', 'OTHERS'))


t = Card('Coin of the Realm', 'Coins of the Realm', 'a Coin of the Realm', 2, 0, 'c2a85c', 'ae6c00', standard_reserve)
standardCards.append(t)

# 252: Disciple
t = Card('Disciple', 'Disciples', 'a Disciple', 5, 1, 'c2bfba', '966a2c', empty)
standardCards.append(t)


# 253: Distant Lands
def distantlands_worth(gS, player):
    playerDeck = gS.crunch(['DECKS', 'OTHERS'], (player))
    DLCard = standardNames.index('Distant Lands')
    for card in playerDeck:
        if standardCards[card].simple_name == 'Distant Lands':
            total = playerDeck[card]
            break

    if DLCard in gS.OTHERS(player):
        return gS.OTHERS(player)[DLCard] / total
    return 0


t = Card('Distant Lands', 'Distant Lands', 'a Distant Lands', 5, 0, '9DA97D', 'c49e8c', standard_reserve, distantlands_worth)
standardCards.append(t)

# 254: Dungeon
t = Card('Dungeon', 'Dungeons', 'a Dungeon', 3, 0, 'dda561', '4f472d', empty)
standardCards.append(t)

# 255: Duplicate
t = Card('Duplicate', 'Duplicates', 'a Duplicate', 4, 0, 'c5af85', '8a887c', standard_reserve)
standardCards.append(t)

# 256: Expedition
t = Card('Expedition', 'Expeditions', 'an Expedition', 3, 2, 'a9a39d', 'ca8c28', empty)
standardCards.append(t)

# 257: Ferry
t = Card('Ferry', 'Ferries', 'a Ferry', 3, 2, 'a9a39d', '798593', empty)
standardCards.append(t)

# 258: Fugitive
t = Card('Fugitive', 'Fugitives', 'a Fugitive', 4, 1, 'c2bfba', '888095', empty)
standardCards.append(t)

# 259: Gear
t = Card('Gear', 'Gears', 'a Gear', 3, 0, 'dda561', '877969', empty)
standardCards.append(t)


# 260: Giant
def giant_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(exc_revealDiscard)
        exc.append(exc_revealTrash)
        exc.append(exc_standardTrash)


t = Card('Giant', 'Giants', 'a Giant', 5, 0, 'c4c0b4', '9c7c5a', giant_action)
standardCards.append(t)

# 261: Guide
t = Card('Guide', 'Guides', 'a Guide', 3, 0, 'c5af85', '486e4a', standard_reserve)
standardCards.append(t)

# 262: Haunted Woods
t = Card('Haunted Woods', 'Haunted Woods', 'a Haunted Woods', 5, 0, 'dda561', '314b39', empty)
standardCards.append(t)

# 263: Hero
t = Card('Hero', 'Heroes', 'a Hero', 5, 1, 'c2bfba', '423732', empty)
standardCards.append(t)

# 264: Hireling
t = Card('Hireling', 'Hirelings', 'a Hireling', 6, 0, 'dda561', '745666', empty)
standardCards.append(t)

# 265: Inheritance
t = Card('Inheritance', 'Inheritances', 'an Inheritance', 7, 2, 'a9a39d', '657759', empty)
standardCards.append(t)

# 266: Lost Arts
t = Card('Lost Arts', 'Lost Arts', 'a Lost Arts', 6, 2, 'a9a39d', 'ab4f1f', empty)
standardCards.append(t)

# 267: Lost City
t = Card('Lost City', 'Lost Cities', 'a Lost City', 5, 0, 'c4c0b4', '969c6c', empty)
standardCards.append(t)


# 268: Magpie
def magpie_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(exc_revealTopdeck)


t = Card('Magpie', 'Magpies', 'a Magpie', 4, 0, 'c4c0b4', '707870', magpie_action)
standardCards.append(t)

# 269: Messenger
t = Card('Messenger', 'Messengers', 'a Messenger', 4, 0, 'c4c0b4', '99afc3', empty)
standardCards.append(t)

# 270: Miser
t = Card('Miser', 'Misers', 'a Miser', 4, 0, 'c4c0b4', '726a60', empty)
standardCards.append(t)

# 271: Mission
t = Card('Mission', 'Missions', 'a Mission', 4, 2, 'a9a39d', '7e767c', empty)
standardCards.append(t)

# 272: Pathfinding
t = Card('Pathfinding', 'Pathfindings', 'a Pathfinding', 8, 2, 'a9a39d', '664820', empty)
standardCards.append(t)

# 273: Page
t = Card('Page', 'Pages', 'a Page', 2, 0, 'c2bfba', '553d33', empty)
standardCards.append(t)

# 274: Peasant
t = Card('Peasant', 'Peasants', 'a Peasant', 2, 0, 'c2bfba', 'cab026', empty)
standardCards.append(t)

# 275: Pilgrimage
t = Card('Pilgrimage', 'Pilgrimages', 'a Pilgrimage', 4, 2, 'a9a39d', '6e4e28', empty)
standardCards.append(t)

# 276: Plan
t = Card('Plan', 'Plans', 'a Plan', 3, 2, 'a9a39d', '6c4630', empty)
standardCards.append(t)

# 277: Port
t = Card('Port', 'Ports', 'a Port', 4, 0, 'c4c0b4', '586c6e', empty)
standardCards.append(t)

# 278: Quest
t = Card('Quest', 'Quests', 'a Quest', 0, 2, 'a9a39d', '685456', empty)
standardCards.append(t)

# 279: Ranger
t = Card('Ranger', 'Rangers', 'a Ranger', 4, 0, 'c4c0b4', '8c7236', empty)
standardCards.append(t)

# 280: Raid
t = Card('Raid', 'Raids', 'a Raid', 5, 0, 'a9a39d', '4f4347', empty)
standardCards.append(t)

# 281: Ratcatcher
t = Card('Ratcatcher', 'Ratcatchers', 'a Ratcatcher', 2, 0, 'c5af85', '655d4f', standard_reserve)
standardCards.append(t)


# 282: Raze
def raze_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(checkMove(['TRASH'], 'INPLAYS', 'TRASH', ['Raze']))
        exc.append(exc_revealDiscard)


t = Card('Raze', 'Razes', 'a Raze', 2, 0, 'c4c0b4', '6b5949', raze_action)
standardCards.append(t)

# 283: Relic
t = Card('Relic', 'Relics', 'a Relic', 5, 0, 'd8c280', '616959', empty)
standardCards.append(t)

# 284: Royal Carriage
t = Card('Royal Carriage', 'Royal Carriages', 'a Royal Carriage', 5, 0, 'c5af85', '9a7450', standard_reserve)
standardCards.append(t)

# 285: Save
def save_action(move, i, bL, moves, cS):
    if str(move.pred) in ['BUY']:
        tExc.append(checkMove(['PUT INHAND'], 'OTHERS', 'HANDS'))

t = Card('Save', 'Saves', 'a Save', 1, 2, 'a9a39d', '814d3b', save_action)
standardCards.append(t)

# 286: Scouting Party
def scoutingparty_action(move, i, bL, moves, cS):
    if str(move.pred) in ['BUY']:
        exc.append(exc_revealTopdeck)
        exc.append(exc_revealDiscard)

t = Card('Scouting Party', 'Scouting Parties', 'a Scouting Party', 2, 0, 'a9a39d', '97875b', scoutingparty_action)
standardCards.append(t)

# 287: Seaway
t = Card('Seaway', 'Seaways', 'a Seaway', 5, 2, 'a9a39d', '7195a3', empty)
standardCards.append(t)

# 288: Soldier
t = Card('Soldier', 'Soldiers', 'a Soldier', 3, 1, 'c2bfba', 'a58e74', empty)
standardCards.append(t)

# 289: Storyteller
t = Card('Storyteller', 'Storytellers', 'a Storyteller', 5, 0, 'c4c0b4', 'ad735f', empty)
standardCards.append(t)

# 290: Swamp Hag
t = Card('Swamp Hag', 'Swamp Hags', 'a Swamp Hag', 5, 0, 'dda561', '8c462e', empty)
standardCards.append(t)


# 291: Teacher
t = Card('Teacher', 'Teachers', 'a Teacher', 6, 1, 'c5af85', 'bb7937', standard_reserve)
standardCards.append(t)

# 292: Travelling Fair
t = Card('Travelling Fair', 'Travelling Fairs', 'a Travelling Fair', 2, 2, 'a9a39d', 'd2942c', empty)
standardCards.append(t)

# 293: Trade
t = Card('Trade', 'Trades', 'a Trade', 5, 2, 'a9a39d', '735941', empty)
standardCards.append(t)

# 294: Training
t = Card('Training', 'Trainings', 'a Training', 6, 2, 'a9a39d', '533f33', empty)
standardCards.append(t)

# 295: Transmogrify
def transmogrify_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(checkMove(['PUT ONTO'], 'INPLAYS', 'OTHERS'))

    if str(move.pred) in ['CALL']:
        tExc.append(checkMove(['GAIN'], 'SUPPLY', 'HANDS'))
        tExc.append(Exception(check(['GAIN']),
                             standardOnGains('HANDS')))

t = Card('Transmogrify', 'Transmogrifies', 'a Transmogrify', 4, 0, 'c5af85', '6e6258', transmogrify_action)
standardCards.append(t)

# 296: Treasure Trove
t = Card('Treasure Trove', 'Treasure Troves', 'a Treasure Trove', 5, 0, 'd8c280', '95795f', empty)
standardCards.append(t)

# 297: Treasure Hunter
t = Card('Treasure Hunter', 'Treasure Hunters', 'a Treasure Hunter', 3, 1, 'c2bfba', '494343', empty)
standardCards.append(t)

# 298: Warrior
def warrior_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(exc_revealDiscard)
        exc.append(checkMove(['TRASH'], 'DISCARDS', 'TRASH'))
        exc.append(exc_standardTrash)


t = Card('Warrior', 'Warriors', 'a Warrior', 4, 1, 'c2bfba', '564543', warrior_action)
standardCards.append(t)


# 299: Wine Merchant
t = Card('Wine Merchant', 'Wine Merchants', 'a Wine Merchant', 5, 0, 'c5af85', '855b31', standard_reserve)
standardCards.append(t)


# 300: Encampment
t = Card('Encampment', 'Encampments', 'an Encampment', 2, 0, 'c4c0b4', '6d4527', empty)
standardCards.append(t)

# 301: Plunder
t = Card('Plunder', 'Plunders', 'a Plunder', 5, 0, 'd8c280', '573E30', empty)
standardCards.append(t)


# 302: Patrician
def patrician_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(exc_revealTopdeck)


t = Card('Patrician', 'Patricians', 'a Patrician', 2, 0, 'c4c0b4', '6a80a0', patrician_action)
standardCards.append(t)

# 303: Emporium
t = Card('Emporium', 'Emporia', 'an Emporium', 5, 0, 'c4c0b4', '50ABDF', empty)
standardCards.append(t)


# 304: Settlers
def settlers_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(checkMove(['PUT INHAND'], 'DISCARDS', 'HANDS'))


t = Card('Settlers', 'Settlers', 'a Settlers', 2, 0, 'c4c0b4', '784624', settlers_action)
standardCards.append(t)


# 305: Bustling Village
def bustvillage_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(checkMove(['PUT INHAND'], 'DISCARDS', 'HANDS'))


t = Card('Bustling Village', 'Bustling Villages', 'a Bustling Village', 5, 0, 'c4c0b4', '745E4D', bustvillage_action)
standardCards.append(t)

# 306: Catapult
t = Card('Catapult', 'Catapults', 'a Catapult', 3, 0, 'c4c0b4', '839f55', empty)
standardCards.append(t)


# 307: Rocks
def rocks_action(move, i, bL, moves, cS):
    if str(move.pred) in ['BUY AND GAIN', 'GAIN TOPDECK',
                            'GAIN TRASH', 'GAIN']:
        if gS[-1].phase == 1:
            exc.append(checkMove(['GAIN'], 'SUPPLY', 'DECKS'))
            exc.append(Exception(check(['GAIN']),
                                 standardOnGains('DECKS')))
        else:
            exc.append(checkMove(['GAIN'], 'SUPPLY', 'HANDS'))
            exc.append(Exception(check(['GAIN']),
                                 standardOnGains('HANDS'))) 


t = Card('Rocks', 'Rocks', 'a Rocks', 4, 0, 'd8c280', '80963a', rocks_action)
standardCards.append(t)


# 308: Gladiator
def gladiator_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(checkMove(['TRASH'], 'SUPPLY', 'TRASH',
                                     ['Gladiator']))


t = Card('Gladiator', 'Gladiators', 'a Gladiator', 3, 0, 'c4c0b4', 'b28674', gladiator_action)
standardCards.append(t)

# 309: Fortune
t = Card('Fortune', 'Fortunes', 'a Fortune', 16, 0, 'd8c280', '94794F', empty)
standardCards.append(t)

# 310: Castles
t = Card('Castles', 'Castles', 'a Castles', 3, 0, '9cbe8a', '2d7bbb', empty)
standardCards.append(t)

castles = ['Humble Castle', 'Crumbling Castle', 'Small Castle',
           'Haunted Castle', 'Opulent Castle', 'Sprawling Castle',
           'Grand Castle', 'King\'s Castle']


# 311: Humble Castle
def humbleCastle_worth(gS, player):
    playerDeck = gS.crunch(['DECKS', 'DISCARDS', 'HANDS',
                            'OTHERS', 'INPLAYS'], (player))
    return sum([playerDeck[item] for item in playerDeck if
                standardCards[item].simple_name in castles])


t = Card('Humble Castle', 'Humble Castles', 'a Humble Castle', 3, -1, 'a9c35d', '63af7f', empty, humbleCastle_worth)
standardCards.append(t)

# 312: Crumbling Castle
t = Card('Crumbling Castle', 'Crumbling Castles', 'a Crumbling Castle', 4, -1, '9cbe8a', 'ceb22c', empty, staticWorth(1))
standardCards.append(t)


# 313: Small Castle
def smallcastle_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(checkMove(['TRASH'], 'INPLAYS', 'TRASH',
                                     ['Small Castle']))


t = Card('Small Castle', 'Small Castles', 'a Small Castle', 5, -1, 'aac298', '96a692', smallcastle_action, staticWorth(2))
standardCards.append(t)

# 314: Haunted Castle
t = Card('Haunted Castle', 'Haunted Castles', 'a Haunted Castle', 6, -1, '9cbe8a', '4a6064', empty, staticWorth(2))
standardCards.append(t)

# 315: Opulent Castle
t = Card('Opulent Castle', 'Opulent Castles', 'an Opulent Castle', 7, -1, 'aac298', '4f9391', empty, staticWorth(3))
standardCards.append(t)

# 316: Sprawling Castle
t = Card('Sprawling Castle', 'Sprawling Castles', 'a Sprawling Castle', 8, -1, '9cbe8a', 'ffb300', empty, staticWorth(4))
standardCards.append(t)

# 317: Grand Castle
t = Card('Grand Castle', 'Grand Castles', 'a Grand Castle', 9, -1, '9cbe8a', '9e7e5a', empty, staticWorth(5))
standardCards.append(t)


# 318: King\'s Castle
def kingsCastle_worth(gS, player):
    playerDeck = gS.crunch(['DECKS', 'DISCARDS', 'HANDS',
                            'OTHERS', 'INPLAYS'], (player))
    return sum([2 * playerDeck[item] for item in playerDeck if
                standardCards[item].simple_name in castles])


t = Card('King\'s Castle', 'King\'s Castles', 'a King\'s Castle', 10, -1, '9cbe8a', 'cd8959', empty, kingsCastle_worth)
standardCards.append(t)

# 319: Advance
t = Card('Advance', 'Advances', 'an Advance', 0, 2, 'a9a39d', '714d41', empty)
standardCards.append(t)

# 320: Annex
t = Card('Annex', 'Annexes', 'an Annex', 8, 2, 'a9a39d', '7a5a36', empty)
standardCards.append(t)


# 321: Archive
def archive_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(checkMove(['SET ASIDE'], 'DECKS', 'OTHERS'))


t = Card('Archive', 'Archives', 'an Archive', 5, 0, 'dda561', '7b5d47', archive_action)
standardCards.append(t)

# 322: Aqueduct
t = Card('Aqueduct', 'Aqueducts', 'an Aqueduct', 0, 2, '65ab6f', '9a905c', empty)
standardCards.append(t)

# 323: Arena
t = Card('Arena', 'Arenas', 'an Arena', 0, 2, '65ab6f', 'b0587c', empty)
standardCards.append(t)


# 324: Bandit Fort
def banditfort_worth(gameState, player):
    playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
    return sum([-2 * playerDeck[item] for item in playerDeck if
                standardCards[item].simple_name in ['Silver', 'Gold']])

t = Card('Bandit Fort', 'Bandit Forts', 'a Bandit Fort', 0, 2, '65ab6f', 'b0a66e', empty, banditfort_worth)
standardCards.append(t)

# 325: Banquet
t = Card('Banquet', 'Banquets', 'a Banquet', 3, 2, 'a9a39d', '6f5735', empty)
standardCards.append(t)

# 326: Basilica
t = Card('Basilica', 'Basilicas', 'a Basilica', 0, 2, '65ab6f', '835945', empty)
standardCards.append(t)

# 327: Baths
t = Card('Baths', 'Baths', 'a Baths', 0, 2, '65ab6f', '746c44', empty)
standardCards.append(t)

# 328: Battlefield
t = Card('Battlefield', 'Battlefields', 'a Battlefield', 0, 2, '65ab6f', '528ec6', empty)
standardCards.append(t)

# 329: Capital
t = Card('Capital', 'Capitals', 'a Capital', 5, 0, 'd8c280', '765648', empty)
standardCards.append(t)

# 330: Charm
t = Card('Charm', 'Charms', 'a Charm', 5, 0, 'd8c280', '756349', empty)
standardCards.append(t)


# 331: Chariot Race
def chariotrace_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(exc_revealTopdeck)

t = Card('Chariot Race', 'Chariot Races', 'a Chariot Race', 3, 0, 'c4c0b4', '7f7569', chariotrace_action)
standardCards.append(t)

# 332: City Quarter
t = Card('City Quarter', 'City Quarters', 'a City Quarter', 8, 0, 'c4c0b4', '7e6a30', empty)
standardCards.append(t)

# 333: Colonnade
t = Card('Colonnade', 'Colonnades', 'a Colonnade', 0, 2, '65ab6f', '9f7b27', empty)
standardCards.append(t)

# 334: Conquest
t = Card('Conquest', 'Conquests', 'a Conquest', 6, 2, 'a9a39d', '7c9692', empty)
standardCards.append(t)

# 335: Crown
t = Card('Crown', 'Crowns', 'a Crown', 5, 0, 'cec28a', '7b4b33', empty)
standardCards.append(t)

# 336: Delve
t = Card('Delve', 'Delves', 'a Delve', 2, 2, 'a9a39d', '716149', empty)
standardCards.append(t)

# 337: Defiled Shrine
t = Card('Defiled Shrine', 'Defiled Shrines', 'a Defiled Shrine', 0, 2, '65ab6f', '5a746e', empty)
standardCards.append(t)

# 338: Dominate
t = Card('Dominate', 'Dominates', 'a Dominate', 14, 2, 'a9a39d', '896b71', empty)
standardCards.append(t)

# 339: Donate
t = Card('Donate', 'Donates', 'a Donate', 8, 2, 'a9a39d', '886c7a', empty)
standardCards.append(t)

# 340: Enchantress
t = Card('Enchantress', 'Enchantresses', 'an Enchantress', 3, 0, 'dda561', 'a5855f', empty)
standardCards.append(t)


# 341: Engineer
def engineer_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        def engineerTrashCondition(cM):
            return cM[0].indent == 0 and \
                   str(move.pred) == 'TRASH' and \
                   cM[0].items.primary() == 'Engineer'

        if cM[0].indent == 0:
            tExc.append(Exception(engineerTrashCondition, moveException('INPLAYS', 'TRASH'), chunkLength(cM) + 2))
            exc.append(checkMove(['TRASH'], 'INPLAYS', 'TRASH', ['Engineer']))
        else:
            exc.append(checkMove(['TRASH'], 'INPLAYS', 'TRASH', ['Engineer']))


t = Card('Engineer', 'Engineers', 'an Engineer', 4, 0, 'c4c0b4', '733719', engineer_action)
standardCards.append(t)


# 342: Farmers' Market
def farmmarket_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(checkMove(['TRASH'], 'INPLAYS', 'TRASH',
                                     ['Farmers\' Market']))


t = Card('Farmers\' Market', 'Farmers\' Markets', 'a Farmers\' Market', 3, 0, 'c4c0b4', '867642', farmmarket_action)
standardCards.append(t)

# 343: Forum
t = Card('Forum', 'Forums', 'a Forum', 5, 0, 'c4c0b4', 'bc9256', empty)
standardCards.append(t)


# 344: Fountain
def fountain_worth(gameState, player):
    playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
    for card in playerDeck:
        if standardCards[card].simple_name == 'Copper':
            if playerDeck[card] >= 10:
                return 15
    return 0


t = Card('Fountain', 'Fountains', 'a Fountain', 0, 0, '65ab6f', '7c5a34', empty, fountain_worth)
standardCards.append(t)

# 345: Groundskeeper
t = Card('Groundskeeper', 'Groundskeepers', 'a Groundskeeper', 5, 0, 'c4c0b4', '978957', empty)
standardCards.append(t)


# 346: Keep
def keep_worth(gameState, player):
    playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
    otherDeck = gameState.crunch(PERSONAL_ZONES, [1 - player])
    total = 0

    for card in playerDeck:
        if standardCards[card].simple_name in treasures:
            if card in otherDeck:
                if playerDeck[card] >= otherDeck[card]:
                    total += 5
            else:
                total += 5

    return total

t = Card('Keep', 'Keeps', 'a Keep', 0, 2, '65ab6f', '6f4f7d', empty, keep_worth)
standardCards.append(t)

# 347: Labyrinth
t = Card('Labyrinth', 'Labyrinths', 'a Labyrinth', 0, 2, '65ab6f', '5e884c', empty)
standardCards.append(t)

# 348: Legionary
t = Card('Legionary', 'Legionaries', 'a Legionary', 5, 0, 'c4c0b4', '714b41', empty)
standardCards.append(t)

# 349: Mountain Pass
t = Card('Mountain Pass', 'Mountain Passes', 'a Mountain Pass', 0, 2, '65ab6f', '657d8d', empty)
standardCards.append(t)


# 350: Museum
def museum_worth(gameState, player):
    playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
    return 2 * len(playerDeck.cardList())

t = Card('Museum', 'Museums', 'a Museum', 0, 2, '65ab6f', 'c47a00', empty, museum_worth)
standardCards.append(t)


# 351: Obelisk
def obelisk_worth(gameState, player):
    playerDeck = gameState.crunch(PERSONAL_ZONES, (player))

    if gameState.obelisk in playerDeck:
        return playerDeck[obelisk]
    else:
        return 0


t = Card('Obelisk', 'Obelisks', 'an Obelisk', 0, 2, '65ab6f', '774d29', empty, obelisk_worth)
standardCards.append(t)


# 352: Orchard
def orchard_worth(gameState, player):
    playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
    total = 0

    for card in playerDeck:
        if standardCards[card].simple_name in actionList:
            if playerDeck[card] >= 3:
                total += 4

    return total


t = Card('Orchard', 'Orchards', 'an Orchard', 0, 2, '65ab6f', '707c5c', empty, orchard_worth)
standardCards.append(t)

# 353: Overlord
t = Card('Overlord', 'Overlords', 'an Overlord', 8, 0, 'c4c0b4', '9a8a90', BoM_action)
standardCards.append(t)

# 354: Palace
def palace_worth(gameState, player):
    playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
    treasures = ['Copper', 'Silver', 'Gold']
    counts = [0, 0, 0]

    for card in playerDeck:
        if standardCards[card].simple_name in treasures:
            counts[treasures.index(standardCards[card].simple_name)] += playerDeck[card]

    return 3 * min(counts)


t = Card('Palace', 'Palaces', 'a Palace', 0, 2, '65ab6f', 'c07442', empty, palace_worth)
standardCards.append(t)

# 355: Ritual
t = Card('Ritual', 'Rituals', 'a Ritual', 4, 2, 'a9a39d', '7a5224', empty)
standardCards.append(t)

# 356: Royal Blacksmith
t = Card('Royal Blacksmith', 'Royal Blacksmiths', 'a Royal Blacksmith', 8, 0, 'c4c0b4', '69452b', empty)
standardCards.append(t)

# 357: Sacrifice
t = Card('Sacrifice', 'Sacrifices', 'a Sacrifice', 4, 0, 'c4c0b4', '9b675f', empty)
standardCards.append(t)

# 358: Salt the Earth
def salt_action(move, i, bL, moves, cS):
    if str(move.pred) in ['BUY']:
        exc.append(Exception(check(['TRASH']), moveException('SUPPLY', 'TRASH')))

t = Card('Salt the Earth', 'Salt the Earths', 'a Salt the Earth', 4, 2, 'a9a39d', '7b8383', salt_action)
standardCards.append(t)

# 359: Tax
t = Card('Tax', 'Taxes', 'a Tax', 2, 2, 'a9a39d', 'a0745a', empty)
standardCards.append(t)

# 360: Temple
t = Card('Temple', 'Temples', 'a Temple', 4, 0, 'c4c0b4', 'd6b452', empty)
standardCards.append(t)

# 361: Tomb
t = Card('Tomb', 'Tombs', 'a Tomb', 0, 2, '65ab6f', '8b8585', empty)
standardCards.append(t)

# 362: Tower
def tower_worth(gameState, player):
    playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
    total = 0

    for card in playerDeck:
        if standardCards[card].supply_type == 0 and\
        card not in gameState.SUPPLY:
            if standardCards[card].simple_name not in victoryCards:
                total += playerDeck[card]

    return total


t = Card('Tower', 'Towers', 'a Tower', 0, 2, '65ab6f', 'bb9b3d', empty, tower_worth)
standardCards.append(t)

# 363: Triumph
t = Card('Triumph', 'Triumphs', 'a Triumph', 5, 2, 'a9a39d', '913d05', empty)
standardCards.append(t)

# 364: Triumphal Arch
def arch_worth(gameState, player):
    playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
    counts = sorted([playerDeck[card] for card in playerDeck if
                     standardCards[card].simple_name in actionList], reverse=True)
    counts = counts + [0, 0]

    return 3 * counts[1]


t = Card('Triumphal Arch', 'Triumphal Arches', 'a Triumphal Arch', 0, 2, '65ab6f', '8f8b51', empty, arch_worth)
standardCards.append(t)

# 365: Villa
t = Card('Villa', 'Villas', 'a Villa', 4, 0, 'c4c0b4', '87b34f', empty)
standardCards.append(t)

# 366: Wall
def wall_worth(gameState, player):
    playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
    size = gameState.crunch(['DECKS', 'HANDS', 'DISCARDS', 'OTHERS', 'INPLAYS'], (player)).count()
    return 15 - max(15, size)

t = Card('Wall', 'Walls', 'a Wall', 0, 2, '65ab6f', '5e4a54', empty, wall_worth)
standardCards.append(t)

# 367: Wolf Den
def den_worth(gameState, player):
    playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
    return -3 * len([card for card in playerDeck if playerDeck[card] == 1])

t = Card('Wolf Den', 'Wolf Dens', 'a Wolf Den', 0, 2, '65ab6f', 'a1a18f', empty, den_worth)
standardCards.append(t)

# 368: Wedding
t = Card('Wedding', 'Weddings', 'a Wedding', 7, 2, 'a9a39d', '715919', empty)
standardCards.append(t)

# 369: Wild Hunt
t = Card('Wild Hunt', 'Wild Hunts', 'a Wild Hunt', 5, 0, 'c4c0b4', '15516f', empty)
standardCards.append(t)

# 370: Windfall
t = Card('Windfall', 'Windfalls', 'a Windfall', 5, 2, 'a9a39d', '9e5402', empty)
standardCards.append(t)

# 371: Boon Drawpile
t = Card('Boon Drawpile', 'Boon Drawpiles', 'a Boon Drawpile', 0, -1, 'dbcf00', '666666', empty)
standardCards.append(t)

# 372: Boon Discardpile
t = Card('Boon Discardpile', 'Boon Discardpiles', 'a Boon Discardpile', 0, -1, 'dbcf00', '666666', empty)
standardCards.append(t)

# 373: The Earth\'s Gift
t = Card('The Earth\'s Gift', 'The Earth\'s Gifts', 'The Earth\'s Gift', 0, -1, 'dbcf00', '6b6733', empty)
standardCards.append(t)

# 374: The Field\'s Gift
t = Card('The Field\'s Gift', 'The Field\'s Gifts', 'The Field\'s Gift', 0, -1, 'dbcf00', 'd3cd17', empty)
standardCards.append(t)

# 375: The Flame\'s Gift
t = Card('The Flame\'s Gift', 'The Flame\'s Gifts', 'The Flame\'s Gift', 0, -1, 'dbcf00', 'ff8f00', empty)
standardCards.append(t)

# 376: The Forest\'s Gift
t = Card('The Forest\'s Gift', 'The Forest\'s Gifts', 'The Forest\'s Gift', 0, -1, 'dbcf00', '3b8d0b', empty)
standardCards.append(t)

# 377: The Moon\'s Gift
t = Card('The Moon\'s Gift', 'The Moon\'s Gifts', 'The Moon\'s Gift', 0, -1, 'dbcf00', '001ee4', empty)
standardCards.append(t)

# 378: The Mountain\'s Gift
t = Card('The Mountain\'s Gift', 'The Mountain\'s Gifts', 'The Mountain\'s Gift', 0, -1, 'dbcf00', '005cff', empty)
standardCards.append(t)

# 379: The River\'s Gift
t = Card('The River\'s Gift', 'The River\'s Gifts', 'The River\'s Gift', 0, -1, 'dbcf00', '4e9c92', empty)
standardCards.append(t)

# 380: The Sea\'s Gift
t = Card('The Sea\'s Gift', 'The Sea\'s Gifts', 'The Sea\'s Gift', 0, -1, 'dbcf00', '0071d7', empty)
standardCards.append(t)

# 381: The Sky\'s Gift
t = Card('The Sky\'s Gift', 'The Sky\'s Gifts', 'The Sky\'s Gift', 0, -1, 'dbcf00', '1cbeff', empty)
standardCards.append(t)

# 382: The Sun\'s Gift
t = Card('The Sun\'s Gift', 'The Sun\'s Gifts', 'The Sun\'s Gift', 0, -1, 'dbcf00', 'fcbe00', empty)
standardCards.append(t)

# 383: The Swamp\'s Gift
t = Card('The Swamp\'s Gift', 'The Swamp\'s Gifts', 'The Swamp\'s Gift', 0, -1, 'dbcf00', '39650b', empty)
standardCards.append(t)

# 384: The Wind\'s Gift
t = Card('The Wind\'s Gift', 'The Wind\'s Gifts', 'The Wind\'s Gift', 0, -1, 'dbcf00', '67d35b', empty)
standardCards.append(t)

# 385: Hex Drawpile
t = Card('Hex Drawpile', 'Hex Drawpiles', 'a Hex Drawpile', 0, -1, '4137df', '666666', empty)
standardCards.append(t)

# 386: Hex Discardpile
t = Card('Hex Discardpile', 'Hex Discardpiles', 'a Hex Discardpile', 0, -1, '4137df', '666666', empty)
standardCards.append(t)

# 387: Bad Omens
t = Card('Bad Omens', 'Bad Omens', 'Bad Omens', 0, -1, '4137df', '4d4135', empty)
standardCards.append(t)

# 388: Delusion
t = Card('Delusion', 'Delusions', 'Delusion', 0, -1, '4137df', '65634d', empty)
standardCards.append(t)

# 389: Envy
t = Card('Envy', 'Envies', 'Envy', 0, -1, '4137df', '618f55', empty)
standardCards.append(t)

# 390: Famine
t = Card('Famine', 'Famines', 'Famine', 0, -1, '4137df', '919f8f', empty)
standardCards.append(t)

# 391: Fear
t = Card('Fear', 'Fears', 'Fear', 0, -1, '4137df', '1f3347', empty)
standardCards.append(t)

# 392: Greed
t = Card('Greed', 'Greeds', 'Greed', 0, -1, '4137df', 'c13f0b', empty)
standardCards.append(t)

# 393: Haunting
t = Card('Haunting', 'Hauntings', 'Haunting', 0, -1, '4137df', '344860', empty)
standardCards.append(t)

# 394: Locusts
t = Card('Locusts', 'Locusts', 'Locusts', 0, -1, '4137df', '43c95f', empty)
standardCards.append(t)

# 395: Misery
t = Card('Misery', 'Miseries', 'Misery', 0, -1, '4137df', '1c161a', empty)
standardCards.append(t)

# 396: Plague
t = Card('Plague', 'Plagues', 'Plague', 0, -1, '4137df', '42aa6c', empty)
standardCards.append(t)

# 397: Poverty
t = Card('Poverty', 'Poverties', 'Poverty', 0, -1, '4137df', '2e2a2a', empty)
standardCards.append(t)

# 398: War
t = Card('War', 'Wars', 'War', 0, -1, '4137df', 'a12700', empty)
standardCards.append(t)

# 399: Miserable
def miserable_action(move, i, bL, moves, cS):
    if str(move.pred) == ['TAKES']:
        gS[-1].vps[cM[0].player] -= 2

t = Card('Miserable', 'Miserables', 'Miserable', 0, -1, 'ceb0a4', '1c161a', miserable_action)
standardCards.append(t)

# 400: Twice Miserable
def twicemiserable_action(move, i, bL, moves, cS):
    if str(move.pred) == ['TAKES']:
        gS[-1].vps[cM[0].player] -= 2

t = Card('Twice Miserable', 'Twice Miserables', 'Twice Miserable', 0, -1, 'ceb0a4', '1c161a', twicemiserable_action)
standardCards.append(t)

# 401: Envious
t = Card('Envious', 'Envious', 'Envious', 0, -1, 'ceb0a4', '618f55', empty)
standardCards.append(t)

# 402: Deluded
t = Card('Deluded', 'Deludeds', 'Deluded', 0, -1, 'ceb0a4', '65634d', empty)
standardCards.append(t)

# 403: Lost In The Woods
t = Card('Lost In The Woods', 'Lost In The Woods', 'Lost In The Woods', 0, -1, 'ceb0a4', '527052', empty)
standardCards.append(t)


# 404: Bard
t = Card('Bard', 'Bards', 'a Bard', 4, 0, 'c4c0b4', '57932f', empty)
standardCards.append(t)


# 405: Blessed Village
t = Card('Blessed Village', 'Blessed Villages', 'a Blessed Village', 4, 0,
         'c4c0b4', '8f7737', empty)
standardCards.append(t)

# 406: Changeling
def changeling_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(exc_inplayTrash)
        exc.append(exc_standardTrash)


t = Card('Changeling', 'Changelings', 'a Changeling', 3, 0, '30484e', '183442', changeling_action)
standardCards.append(t)

# 407: Cemetery
t = Card('Cemetery', 'Cemeteries', 'a Cemetery', 4, 0, '9cbe8a', '53735b', empty, staticWorth(2))
standardCards.append(t)

# 408: Cobbler
t = Card('Cobbler', 'Cobblers', 'a Cobbler', 5, 0, '7a5622', '5a501c', empty)
standardCards.append(t)

# 409: Conclave
t = Card('Conclave', 'Conclaves', 'a Conclave', 4, 0, 'c4c0b4', '9c6a14', empty)
standardCards.append(t)

# 410: Crypt
t = Card('Crypt', 'Crypts', 'a Crypt', 5, 0, '7a5622', '0d494f', empty)
standardCards.append(t)

# 411: Cursed Village
t = Card('Cursed Village', 'Cursed Villages', 'a Cursed Village', 5, 0,
         'c4c0b4', '265ea6', empty)
standardCards.append(t)


# 412: Den Of Sin
t = Card('Den Of Sin', 'Dens Of Sin', 'a Den Of Sin', 5, 0, '7a5622', '2c2226', empty)
standardCards.append(t)

# 413: Devil\'s Workshop
t = Card('Devil\'s Workshop', 'Devil\'s Workshops', 'a Devil\'s Workshop', 4, 0, '30484e', '7d5b83', empty)
standardCards.append(t)


# 414: Druid
def druid_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        whichBoon = standardCards[CARD_CARD]
        exc.append(Exception(check('RECEIVE BOONHEX'), empty))
        for subchunk in cM[1:]:
            if subchunk[0].predName() in ['RECEIVE BOONHEX', 'TAKES BOONHEX']:
                whichBoon = subchunk[0].items.primary()
                break
            exc.append(checkMove(['TRASH'], 'INPLAYS', 'TRASH'))

        if whichBoon == 'The Sun\'s Gift':
            exc.append(exc_revealTopdeck)
            exc.append(exc_revealDiscard)

        elif whichBoon == 'The Moon\'s Gift':
            exc.append(exc_harbinger)


t = Card('Druid', 'Druids', 'a Druid', 2, 0, 'c4c0b4', '49b921', druid_action)
standardCards.append(t)

# 415: Exorcist
t = Card('Exorcist', 'Exorcists', 'an Exorcist', 4, 0, '30484e', '3763b5', empty)
standardCards.append(t)


# 416: Faithful Hound
def hound_action(move, i, bL, moves, cS):
    if str(move.pred) in ['REACT']:
        tExc.append(checkMove(['SET ASIDE'], 'DISCARDS', 'OTHERS', ['Faithful Hound']))


t = Card('Faithful Hound', 'Faithful Hounds', 'a Faithful Hound', 2, 0, '8ca2be', '8c7640', hound_action)
standardCards.append(t)

# 417: Fool
t = Card('Fool', 'Fools', 'a Fool', 3, 0, 'c4c0b4', 'a7af3f', empty)
standardCards.append(t)

# 418: Ghost Town
t = Card('Ghost Town', 'Ghost Towns', 'a Ghost Town', 3, 0, '7a5622', '173b57', empty)
standardCards.append(t)

# 419: Guardian
t = Card('Guardian', 'Guardians', 'a Guardian', 2, 0, '7a5622', '376db9', empty)
standardCards.append(t)

# 420: Idol
t = Card('Idol', 'Idols', 'a Idol', 5, 0, 'd8c280', 'b13700',empty)
standardCards.append(t)

# 421: Leprechaun
t = Card('Leprechaun', 'Leprechauns', 'a Leprechaun', 3, 0, 'c4c0b4', '5e7c04', empty)
standardCards.append(t)


# 422: Monastery
def monastery_action(move, i, bL, moves, cS):
    #Possible conflicts: Exorcist - hence, trash inplay first.
    if str(move.pred) in PLAY_PREDS:
        def monastery_trash(move, i, bL, moves, cS):
            copperID = standardNames.index('Copper')

            if copperID in cM[0].items:
                coppersToKill = cM[0].items[copperID]
            else:
                coppersToKill = 0

            if copperID in gS[-1].INPLAYS[cM[0].player]:
                inPlayCoppers = gS[-1].INPLAYS[cM[0].player][copperID]
            else:
                inPlayCoppers = 0

            coppersToKill = min(coppersToKill, inPlayCoppers)

            if coppersToKill > 0:
                copperStack = Cardstack({copperID: coppersToKill})
                itemsSansCoppers = cM[0].items - copperStack

                gS[-1].move(cM[0].player, 'HANDS', 'TRASH', itemsSansCoppers)
                gS[-1].move(cM[0].player, 'INPLAYS', 'TRASH', copperStack)
            else:
                standardMove('HANDS', 'TRASH', cM, gS)

        exc.append(Exception(check(['TRASH'], ['Copper']),
                             monastery_trash))
        exc.append(exc_standardTrash)


t = Card('Monastery', 'Monasteries', 'a Monastery', 2, 0, '30484e', '02268a', monastery_action)
standardCards.append(t)


# 423: Necromancer
def necromancer_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(checkMove(['PLAY'], 'TRASH', 'TRASH'))
        exc.append(Exception(check(['PLAY']),  standardOnPlay))


t = Card('Necromancer', 'Necromancers', 'a Necromancer', 4, 0, 'c4c0b4', '525a36', necromancer_action)
standardCards.append(t)


# 424: Night Watchman
def watchman_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(exc_revealDiscard)
        exc.append(exc_revealTopdeck)


t = Card('Night Watchman', 'Night Watchmen', 'a Night Watchman', 3, 0, '30484e', '464266', watchman_action)
standardCards.append(t)


# 425: Pixie
def pixie_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        whichBoon = standardCards[CARD_CARD]
        exc.append(Exception(check('RECEIVE BOONHEX'), empty))
        for subchunk in cM[1:]:
            if subchunk[0].predName() in ['RECEIVE BOONHEX', 'TAKES BOONHEX']:
                whichBoon = subchunk[0].items.primary()
                break

        if whichBoon == 'The Flame\'s Gift':
            pixieStack = Cardstack({standardNames.index('Pixie'): 1})
            otherThings = cM[0].items - pixieStack

            def pixieTrash(pixieStack, otherThings):
                def out_function(move, i, bL, moves, cS):
                    gS[-1].move(cM[0].player, 'INPLAYS', 'TRASH',
                                        pixieStack)
                    gS[-1].move(cM[0].player, 'HANDS', 'TRASH',
                                        otherThings)
                return out_function

            exc.append(Exception(check(['TRASH'], ['Pixie']),
                                 pixieTrash(pixieStack, otherThings)))
            exc.append(Exception(check(['TRASH'], ['Pixie']), standardOnTrash))
        else:
            exc.append(checkMove(['TRASH'], 'INPLAYS', 'TRASH'))

            if whichBoon == 'The Sun\'s Gift':
                exc.append(exc_revealTopdeck)
                exc.append(exc_revealDiscard)

            elif whichBoon == 'The Moon\'s Gift':
                exc.append(exc_harbinger)


t = Card('Pixie', 'Pixies', 'a Pixie', 2, 0, 'c4c0b4', 'a9db75', pixie_action)
standardCards.append(t)

# 426: Pooka
t = Card('Pooka', 'Pookas', 'a Pooka', 5, 0, 'c4c0b4', '6b6700', empty)
standardCards.append(t)

# 427: Raider
t = Card('Raider', 'Raiders', 'a Raider', 6, 0, '7a5622', '00238b', empty)
standardCards.append(t)

# 428: Sacred Grove
t = Card('Sacred Grove', 'Sacred Groves', 'a Sacred Grove', 5, 0, 'c4c0b4', '5e7632', druid_action)
standardCards.append(t)

# 429: Secret Cave
t = Card('Secret Cave', 'Secret Caves', 'a Secret Cave', 3, 0, 'dda561', 'be741c', empty)
standardCards.append(t)

# 430: Shepherd
t = Card('Shepherd', 'Shepherds', 'a Shepherd', 4, 0, 'c4c0b4', '9caa90', empty)
standardCards.append(t)

# 431: Skulk
t = Card('Skulk', 'Skulks', 'a Skulk', 4, 0, 'c4c0b4', '7e6060', empty)
standardCards.append(t)

# 432: Tormentor
t = Card('Tormentor', 'Tormentors', 'a Tormentor', 5, 0, 'c4c0b4', '884c6a', empty)
standardCards.append(t)


# 433: Tragic Hero
def tragichero_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(checkMove(['TRASH'], 'INPLAYS', 'TRASH',
                                     ['Tragic Hero', 'Overlord']))


t = Card('Tragic Hero', 'Tragic Heroes', 'a Tragic Hero', 5, 0, 'c4c0b4', '5c88a4', tragichero_action)
standardCards.append(t)

# 434: Tracker
t = Card('Tracker', 'Trackers', 'a Tracker', 2, 0, 'c4c0b4', '87c7d9', empty)
standardCards.append(t)


# 435: Vampire
def vampire_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(checkMove(['RETURN'], 'INPLAYS', 'SUPPLY',
                                     ['Vampire']))

        standard_boonhex(cM, gS, exc, tExc, pers)


t = Card('Vampire', 'Vampires', 'a Vampire', 5, 0, '30484e', '523a4c', vampire_action)
standardCards.append(t)

# 436: Werewolf
t = Card('Werewolf', 'Werewolves', 'a Werewolf', 5, 0, '30484e', '9f8193', empty)
standardCards.append(t)

# 437: Cursed Gold
t = Card('Cursed Gold', 'Cursed Golds', 'a Cursed Gold', 4, 2, 'd8c280', '7D4D22', empty)
standardCards.append(t)

# 438: Goat
t = Card('Goat', 'Goats', 'a Goat', 2, 2, 'd8c280', 'a1e15d', empty)
standardCards.append(t)

# 439: Haunted Mirror
t = Card('Haunted Mirror', 'Haunted Mirrors', 'a Haunted Mirror', 0, 2, 'd8c280', '4F302B', empty)
standardCards.append(t)

# 440: Lucky Coin
t = Card('Lucky Coin', 'Lucky Coins', 'a Lucky Coin', 4, 2, 'd8c280', '9ed654', empty)
standardCards.append(t)


# 441: Magic Lamp
def lamp_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(checkMove(['TRASH'], 'INPLAYS', 'TRASH',
                                     ['Magic Lamp']))


t = Card('Magic Lamp', 'Magic Lamps', 'a Magic Lamp', 0, 2, 'd8c280', '8c3400', lamp_action)
standardCards.append(t)


# 442: Pasture
def pasture_worth(gameState, player):
    playerDeck = gameState.crunch(['DECKS', 'DISCARDS', 'HANDS',
                                   'OTHERS', 'INPLAYS'], (player))
    for card in playerDeck:
        if standardCards[card].simple_name == 'Estate':
            return playerDeck[card]

    return 0


t = Card('Pasture', 'Pastures', 'a Pasture', 2, 2, 'a9c35d', '959D8D', empty, pasture_worth)
standardCards.append(t)

# 443: Pouch
t = Card('Pouch', 'Pouches', 'a Pouch', 2, 2, 'd8c280', '4A4A55', empty)
standardCards.append(t)


# 444: Bat
def bat_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(checkMove(['RETURN'], 'INPLAYS', 'SUPPLY', ['Bat']))


t = Card('Bat', 'Bats', 'a Bat', 2, 1, '30484e', '475B5D', bat_action)
standardCards.append(t)


# 445: Ghost
def ghost_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(exc_revealDiscard)
        exc.append(checkMove(['SET ASIDE'], 'DECKS', 'OTHERS'))


t = Card('Ghost', 'Ghosts', 'a Ghost', 4, 1, '7a5622', '13b12f', ghost_action)
standardCards.append(t)


# 446: Imp
t = Card('Imp', 'Imps', 'an Imp', 2, 1, 'c4c0b4', '936d69', empty)
standardCards.append(t)


# 447: Will-o'-wisp
def wisp_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(exc_revealTopdeck)


t = Card('Will-o\'-wisp', 'Will-o\'-wisps', 'a Will-o\'-wisp', 0, 1, 'c4c0b4', '1d593f', wisp_action)
standardCards.append(t)


# 448: Wish
def wish_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(checkMove(['GAIN'], 'SUPPLY', 'HANDS',))
        exc.append(Exception(check(['GAIN']),
                             standardOnGains('HANDS')))


t = Card('Wish', 'Wishes', 'a Wish', 0, 1, 'c4c0b4', '0f6551', wish_action)
standardCards.append(t)

# 449: Zombie Apprentice
t = Card('Zombie Apprentice', 'Zombie Apprentices', 'a Zombie Apprentice', 3, 1, 'c4c0b4', '292d23', empty)
standardCards.append(t)

# 450: Zombie Mason
def zombiemason_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(checkMove(['TRASH'], 'DECKS', 'TRASH'))
        exc.append(exc_standardTrash)

t = Card('Zombie Mason', 'Zombie Masons', 'a Zombie Mason', 3, 1, 'c4c0b4', '5f513d', zombiemason_action)
standardCards.append(t)

# 451: Zombie Spy
def zombiespy_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(exc_revealDiscard)
        exc.append(exc_revealTopdeck)

t = Card('Zombie Spy', 'Zombie Spies', 'a Zombie Spy', 3, 1, 'c4c0b4', '363438', zombiespy_action)
standardCards.append(t)

# 452: Avanto
t = Card('Avanto', 'Avantos', 'an Avanto', 5, 0, 'c4c0b4', '9fa3af', empty)
standardCards.append(t)

# 453: Black Market
t = Card('Black Market', 'Black Markets', 'a Black Market', 3, 0, 'c4c0b4', 'b5b5b5', empty)
standardCards.append(t)

# 454: Envoy
def envoy_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(exc_revealDiscard)

t = Card('Envoy', 'Envoys', 'an Envoy', 4, 0, 'c4c0b4', '425064', envoy_action)
standardCards.append(t)

# 455: Governor
t = Card('Governor', 'Governors', 'a Governor', 5, 0, 'c4c0b4', '8f9989', empty)
standardCards.append(t)

# 456: Prince
def prince_action(move, i, bL, moves, cS):
    if str(move.pred) in PLAY_PREDS:
        exc.append(checkMove(['SET ASIDE'], 'HANDS', 'OTHERS'))

t = Card('Prince', 'Princes', 'a Prince', 8, 0, 'c4c0b4', 'a4863c', prince_action)
standardCards.append(t)

# 457: Sauna
t = Card('Sauna', 'Saunas', 'a Sauna', 5, 0, 'c4c0b4', '9f8d7b', empty)
standardCards.append(t)

# 458: Stash
t = Card('Stash', 'Stashes', 'a Stash', 5, 0, 'd8c280', '666666', empty)
standardCards.append(t)

# 459: Summon
def summon_action(move, i, bL, moves, cS):
    if str(move.pred) in ['BUY']:
        exc.append(checkMove(['SET ASIDE'], 'SUPPLY', 'OTHERS'))

t = Card('Summon', 'Summons', 'a Summon', 5, 0, 'a9a39d', 'c19b59', summon_action)
standardCards.append(t)

# 460: Walled Village
t = Card('Walled Village', 'Walled Villages', 'a Walled Village', 4, 0, 'c4c0b4', '6eaa70', empty)
standardCards.append(t)

# 461: Black Market Deck
t = Card('Black Market Deck', 'Black Market Decks', 'a Black Market Deck', 0, 0, '666666', '666666', empty)
standardCards.append(t)

# 462: Dismantle
t = Card('Dismantle', 'Dismantles', 'a Dismantle', 4, 0, 'c4c0b4', '8DAEB6', empty)
standardCards.append(t)

# 463: Debt
t = Card('Debt', 'Debt', '1 Debt', 0, 0, 'C73400', 'A02900', empty)
standardCards.append(t)

# 464: Lowercase Debt
t = Card('debt', 'debt', '1 debt', 0, 0, 'C73400', 'A02900', empty)
standardCards.append(t)


# 0
t = Pred("^Game #(.*), (.*)\.$", empty, "GAME START")
standardPreds.append(t)


# 1
def newTurnAction(move, i, bL, moves, cS):
    for i in range(2):
        gS[-1].coins[i] = 0
        gS[-1].coinsLower[i] = 0
    gS[-1].activePlayer = cM[0].player
    gS[-1].phase = 0


t = Pred("^Turn (?P<cards>.*) - (?P<player>.*)$", newTurnAction, "NEW TURN")
standardPreds.append(t)


def standardGains(source, destination='DISCARDS'):
    def out_function(move, i, bL, moves, cS):
        targetStuff = deepcopy(cM[0].items)

        for card in targetStuff:
            if standardCards[card].simple_name in ['Nomad Camp']:
                exceptionalStuff = Cardstack({card: targetStuff[card]})
                targetStuff -= exceptionalStuff

                gS[-1].move(cM[0].player, source, 'DECKS', exceptionalStuff)
                standardOnGains('DECKS')(cM, gS, exc, tExc, pers)

            if standardCards[card].simple_name in ['Den of Sin', 'Guardian',
                                                   'Ghost Town', 'Night Watchman']:
                exceptionalStuff = Cardstack({card: targetStuff[card]})
                targetStuff -= exceptionalStuff

                gS[-1].move(cM[0].player, source, 'HANDS', exceptionalStuff)
                standardOnGains('HANDS')(cM, gS, exc, tExc, pers)

        if targetStuff.count() > 0:
            for card in targetStuff:
                cardStuff = Cardstack({card: targetStuff[card]})
                gS[-1].move(cM[0].player, source, destination, cardStuff)
                standardOnGains(destination)(cM, gS, exc, tExc, pers)

    return out_function


# 2
def buyAndGainAction(move, i, bL, moves, cS):
    standardGains('SUPPLY')(cM, gS, exc, tExc, pers)
    gS[-1].phase = 1


t = Pred("^(?P<player>.*) buys and gains (?P<cards>.*)\.$", buyAndGainAction, "BUY AND GAIN")
standardPreds.append(t)

# 3
t = Pred("^(?P<player>.*) gains (?P<cards>.*) onto their drawpile\.$", standardGains('SUPPLY', 'DECKS'), "GAIN TOPDECK")
standardPreds.append(t)

# 4
t = Pred("^(?P<player>.*) gains (?P<cards>.*) from trash\.$", standardGains('TRASH'), "GAIN TRASH")
standardPreds.append(t)

# 5
t = Pred("^(?P<player>.*) gains (?P<cards>.*)\.$", standardGains('SUPPLY'), "GAIN")
standardPreds.append(t)

# 6
t = Pred("^(?P<player>.*) trashes nothing\.$", empty, "TRASH NOTHING")
standardPreds.append(t)


def pred7Action(move, i, bL, moves, cS):
    # Mining Village Bug
    if cM[0].items.primary() == 'Mining Village' and cM[0].indent == 0:
        gS[-1].move(cM[0].player, 'INPLAYS', 'TRASH', cM[0].items)
    else:
        gS[-1].move(cM[0].player, 'HANDS', 'TRASH', cM[0].items)

    # Market Square
    exc.append(checkMove(['DISCARD'], 'HANDS', 'DISCARDS',
                                 ['Market Square']))


# 7 Trashing
t = Pred("^(?P<player>.*) trashes (?P<cards>.*)\.$", pred7Action, "TRASH")
standardPreds.append(t)


def pred8Action(move, i, bL, moves, cS):
    if cM[0].items.count() > 0:
        gS[-1].move(cM[0].player, 'HANDS', 'DISCARDS', cM[0].items)


# 8 Discards
t = Pred("^(?P<player>.*) discards (?P<cards>.*)\.$", pred8Action, "DISCARD")
standardPreds.append(t)


# 9
t = Pred("^(?P<player>.*) plays (?P<cards>.*) again\.$", empty, "PLAY AGAIN")
standardPreds.append(t)


# 10
t = Pred("^(?P<player>.*) plays (?P<cards>.*) a third time\.$", empty, "PLAY THIRD")
standardPreds.append(t)


# 11
def pred11Action(move, i, bL, moves, cS):
    gS[-1].move(cM[0].player, 'HANDS', 'INPLAYS', cM[0].items)

t = Pred("^(?P<player>.*) plays (?P<cards>.*)\.$", pred11Action, "PLAY")
standardPreds.append(t)

# 12
def pred12Action(move, i, bL, moves, cS):
    if cM[0].indent == 0:
        # Probably Scheme (or walled village / alch / treasury)
        gS[-1].move(cM[0].player, 'INPLAYS', 'DECKS', cM[0].items)

    else:
        gS[-1].move(cM[0].player, 'HANDS', 'DECKS', cM[0].items)

t = Pred("^(?P<player>.*) topdecks (?P<cards>.*)\.$", pred12Action, "TOPDECK")
standardPreds.append(t)

# 13
def pred13Action(move, i, bL, moves, cS):
    gS[-1].move(cM[0].player, 'DECKS', 'HANDS', cM[0].items)

t = Pred("^(?P<player>.*) draws (?P<cards>.*) \(Wharf\)\.$", pred13Action, "WHARF DRAW")
standardPreds.append(t)

# 14
def pred14Action(move, i, bL, moves, cS):
    gS[-1].move(cM[0].player, 'DECKS', 'HANDS', cM[0].items)

t = Pred("^(?P<player>.*) draws (?P<cards>.*) \(Hireling\)\.$", pred14Action, "HIRELING DRAW")
standardPreds.append(t)

# 15
def pred15Action(move, i, bL, moves, cS):
    gS[-1].move(cM[0].player, 'DECKS', 'HANDS', cM[0].items)

t = Pred("^(?P<player>.*) draws (?P<cards>.*) \(Enchantress\)\.$", pred15Action, "WOODS DRAW")
standardPreds.append(t)

# 16
def pred16Action(move, i, bL, moves, cS):
    gS[-1].move(cM[0].player, 'DECKS', 'HANDS', cM[0].items)

t = Pred("^(?P<player>.*) draws (?P<cards>.*) \(Haunted Woods\)\.$", pred16Action, "ENCHANTRESS DRAW")
standardPreds.append(t)

# 17
def pred17Action(move, i, bL, moves, cS):
    gS[-1].move(cM[0].player, 'DECKS', 'HANDS', cM[0].items)

t = Pred("^(?P<player>.*) draws (?P<cards>.*) \(Caravan\)\.$", pred17Action, "CARAVAN DRAW")
standardPreds.append(t)

# 18
def pred18Action(move, i, bL, moves, cS):
    gS[-1].move(cM[0].player, 'DECKS', 'HANDS', cM[0].items)

t = Pred("^(?P<player>.*) gets \+1 Buy, \+1 Action and draws (?P<cards>.*) \(Tactician\)\.$", pred18Action, "TACTICIAN DRAW")
standardPreds.append(t)

# 19
def pred19Action(move, i, bL, moves, cS):
    gS[-1].move(cM[0].player, 'DECKS', 'HANDS', cM[0].items)

t = Pred("^(?P<player>.*) draws (?P<cards>.*) \(from (.*)\)$", pred19Action, "DRAW FROM")
standardPreds.append(t)

# 20
def pred20Action(move, i, bL, moves, cS):
    gS[-1].move(cM[0].player, 'DECKS', 'HANDS', cM[0].items)

t = Pred("^(?P<player>.*) draws (?P<cards>.*) \(Ghost Town\)\.$", pred20Action, "GT DRAW")
standardPreds.append(t)

# 21
def pred21Action(move, i, bL, moves, cS):
    activePlayer = gS[-1].activePlayer
    # Cleanup
    if cM[0].isCleanup:
        if cM[0].player == activePlayer:
            gS[-1].move(cM[0].player, 'INPLAYS', 'DISCARDS', gS[-1].INPLAYS[cM[0].player])
            gS[-1].move(cM[0].player, 'HANDS', 'DISCARDS', gS[-1].HANDS[cM[0].player])

    gS[-1].move(cM[0].player, 'DECKS', 'HANDS', cM[0].items)

t = Pred("^(?P<player>.*) draws (?P<cards>.*)\.$", pred21Action, "DRAW")
standardPreds.append(t)

# 22
t = Pred("^(?P<player>.*) wishes for (?P<cards>.*) but reveals (.*)\.$", empty, "WISH FAIL")
standardPreds.append(t)

# 23
t = Pred("^(?P<player>.*) reveals (?P<cards>.*)\.$", empty, "REVEAL")
standardPreds.append(t)

# 24
t = Pred("^(?P<player>.*) looks at (?P<cards>.*)\.$", empty, "LOOK")
standardPreds.append(t)

# 25
def pred25Action(move, i, bL, moves, cS):
    if cM[0].indent == 0 and cM[0].items.primary() == 'Faithful Hound':
        gS[-1].move(cM[0].player, 'OTHERS', 'HANDS', cM[0].items)
    else:
        # Villa's handled somewhere else
        if cM[0].items.primary() != 'Villa':
            gS[-1].move(cM[0].player, 'DECKS', 'HANDS', cM[0].items)

t = Pred("^(?P<player>.*) puts (?P<cards>.*) into their hand\.$", pred25Action, "PUT INHAND")
standardPreds.append(t)

# 26
def pred26Action(move, i, bL, moves, cS):
    if cM[0].items.primary() not in BOONHEX:
        gS[-1].move(cM[0].player, 'INPLAYS', 'OTHERS', cM[0].items)

t = Pred("^(?P<player>.*) sets (?P<cards>.*) aside\.$", pred26Action, "SET ASIDE")
standardPreds.append(t)

# 27
def pred27Action(move, i, bL, moves, cS):
    gS[-1].move(cM[0].player, 'HANDS', 'OTHERS', cM[0].items)

t = Pred("^(?P<player>.*) puts (?P<cards>.*) on their (.*)\.$", pred27Action, "PUT ONTO")
standardPreds.append(t)

# 28
def pred28Action(move, i, bL, moves, cS):
    gS[-1].move(cM[0].player, 'OTHERS', 'INPLAYS', cM[0].items)

t = Pred("^(?P<player>.*) calls (?P<cards>.*)\.$", pred28Action, "CALL")
standardPreds.append(t)

# 29
def pred29Action(move, i, bL, moves, cS):
    gS[-1].move(cM[0].player, 'DECKS', 'DISCARDS', gS[-1].DECKS[cM[0].player])

t = Pred("^(?P<player>.*) moves their deck to the discard\.$", pred29Action, "DISCARD DECK")
standardPreds.append(t)

# 30
t = Pred("^(?P<player>.*) puts (?P<cards>.*) back onto their deck\.$", empty, "RETURN TOPDECK")
standardPreds.append(t)

# 31
def pred31Action(move, i, bL, moves, cS):
    gS[-1].move(cM[0].player, 'DISCARDS', 'DECKS', cM[0].items)

t = Pred("^(?P<player>.*) shuffles (?P<cards>.*) into their deck\.$", pred31Action, "SHUFFLE INTO")
standardPreds.append(t)

# 32
t = Pred("^(?P<player>.*) inserts (?P<cards>.*) into their deck\.$", empty, "INSERT INTO")
standardPreds.append(t)

# 33
def pred33Action(move, i, bL, moves, cS):
    gS[-1].move(cM[0].player, 'INPLAYS', 'SUPPLY', cM[0].items)

t = Pred("^(?P<player>.*) returns (?P<cards>.*) to (.*)\.$", pred33Action, "RETURN TO")
standardPreds.append(t)

# 34
t = Pred("^(?P<player>.*) returns (?P<cards>.*) set by (.*)\.$", empty, "RETURN SETBY")
standardPreds.append(t)

# 35
def pred35Action(move, i, bL, moves, cS):
    gS[-1].move(cM[0].player, 'HANDS', 'SUPPLY', cM[0].items)

t = Pred("^(?P<player>.*) returns (?P<cards>.*)\.$", pred35Action, "RETURN")
standardPreds.append(t)

# 36
def pred36Action(move, i, bL, moves, cS):
    gS[-1].move(cM[0].player, 'SUPPLY', 'DISCARDS', cM[0].items)

t = Pred("^(?P<player>.*) receives (?P<cards>.*)\.$", pred36Action, "RECEIVE.")
standardPreds.append(t)


# 37
def standard_boonhex(move, i, bL, moves, cS):
    whichBoon = cM[0].items.primary()

    def removeBoonhex(exceptions):
        def out_function(move, i, bL, moves, cS):
            for exception in exceptions:
                if exception in tExc:
                    tExc.remove(exception)
        return out_function

    def discardBoonhexCondition(cM):
        return cM[0].items.primary() == whichBoon and str(move.pred) == 'DISCARD'

    elevated_topdeck = Exception(check(['TOPDECK']),
                                 moveException('DECKS', 'DECKS'),
                                 priority=1)
    elevated_trash = Exception(check(['TRASH']),
                               moveException('DECKS', 'TRASH'),
                               priority=1)
    elevated_harbinger = Exception(check(['TOPDECK']),
                                   moveException('DISCARDS', 'DECKS'),
                                   priority=1)

    if whichBoon == 'The Sun\'s Gift':
        tExc.append(elevated_topdeck)
        tExc.append(exc_revealDiscard)
        tExc.append(Exception(discardBoonhexCondition,
                    removeBoonhex([elevated_topdeck, exc_revealDiscard])))

    elif whichBoon == 'The Moon\'s Gift':
        tExc.append(elevated_harbinger)
        tExc.append(Exception(discardBoonhexCondition,
                    removeBoonhex([elevated_harbinger])))

    elif whichBoon == 'Locusts':
        tExc.append(elevated_trash)
        tExc.append(Exception(discardBoonhexCondition,
                    removeBoonhex([elevated_trash])))

    elif whichBoon == 'War':
        tExc.append(elevated_trash)
        tExc.append(exc_revealDiscard)
        tExc.append(Exception(discardBoonhexCondition,
                    removeBoonhex([elevated_trash, exc_revealDiscard])))

    elif whichBoon == 'Greed':
        greed_gain = checkMove(['GAIN'], 'SUPPLY', 'DECKS', ['Copper'])
        copperStack = Cardstack({standardNames.index('Copper'): 1})
        greed_ongain = Exception(check(['GAIN'], ['Copper']),
                                 standardOnGains('DECKS'))
        tExc.append(greed_gain)
        tExc.append(greed_ongain)
        tExc.append(Exception(discardBoonhexCondition,
                    removeBoonhex([greed_ongain, greed_gain])))

    elif whichBoon == 'Plague':
        plague_gain = checkMove(['GAIN'], 'SUPPLY', 'HANDS', ['Curse'])
        curseStack = Cardstack({standardNames.index('Curse'): 1})
        plague_ongain = Exception(check(['GAIN'], ['Copper']),
                                  standardOnGains('HANDS'))
        tExc.append(plague_gain)
        tExc.append(plague_ongain)
        tExc.append(Exception(discardBoonhexCondition,
                    removeBoonhex([plague_ongain, plague_gain])))

    elif whichBoon == 'Bad Omens':
        tExc.append(elevated_harbinger)
        tExc.append(exc_revealDiscard)
        tExc.append(Exception(discardBoonhexCondition,
                    removeBoonhex([elevated_harbinger, exc_revealDiscard])))

    elif whichBoon == 'Famine':
        tExc.append(exc_revealDiscard)
        famine_discard = checkMove(['SHUFFLE INTO'], 'DECKS', 'DECKS')
        tExc.append(famine_discard)
        tExc.append(Exception(discardBoonhexCondition,
                    removeBoonhex([exc_revealDiscard, famine_discard])))


t = Pred("^(?P<player>.*) receives (?P<cards>.*)$", standard_boonhex, "RECEIVE BOONHEX")
standardPreds.append(t)


# 38
def passAction(move, i, bL, moves, cS):
    gS[-1].HANDS[cM[0].player] -= cM[0].items
    gS[-1].HANDS[1 - cM[0].player] += cM[0].items


t = Pred("^(?P<player>.*) passes (?P<cards>.*) to (.*)\.$", passAction, "PASS")
standardPreds.append(t)


# 39
def pred39Action(move, i, bL, moves, cS):
    gS[-1].move(cM[0].player, 'SUPPLY', 'DECKS', cM[0].items)


t = Pred("^(?P<player>.*) starts with (?P<cards>.*)\.$", pred39Action, "STARTS")
standardPreds.append(t)

# 40
t = Pred("^(?P<player>.*) buys Alms but has (?P<cards>.*) in play\.$", empty, "ALMS FAIL")
standardPreds.append(t)

# 41
t = Pred("^(?P<player>.*) buys Borrow but already had (?P<cards>.*)$", empty, "BORROW FAIL")
standardPreds.append(t)


# 42
def buyAction(move, i, bL, moves, cS):
    gS[-1].phase = 1


t = Pred("^(?P<player>.*) buys (?P<cards>.*)\.$", empty, "BUY")
standardPreds.append(t)

# 43
t = Pred("^COUNTER_ADD$", empty, "COUNTER ADD")
standardPreds.append(t)

# 44
t = Pred("^COUNTER_RESET$", empty, "COUNTER RESET")
standardPreds.append(t)

# 45
t = Pred("^(?P<player>.*) reacts with (?P<cards>.*)\.$", empty, "REACT")
standardPreds.append(t)

# 46
def pred46Action(move, i, bL, moves, cS):
    activePlayer = cM[0].player
    # Cleanup
    if cM[0].isCleanup:
        gS[-1].move(activePlayer, 'INPLAYS', 'DISCARDS', gS[-1].INPLAYS[activePlayer])
        gS[-1].move(activePlayer, 'HANDS', 'DISCARDS', gS[-1].HANDS[activePlayer])

    gS[-1].move(activePlayer, 'DISCARDS', 'DECKS', gS[-1].DISCARDS[activePlayer])

t = Pred("^(?P<player>.*) shuffles their deck\.$", pred46Action, "SHUFFLE")
standardPreds.append(t)

# 47
def pred47Action(move, i, bL, moves, cS):
    gS[-1].move(cM[0].player, 'DECKS', 'HANDS', Cardstack({cM[0].items.cardList()[0]: 1}))

t = Pred("^(?P<player>.*) wishes for (?P<cards>.*) and finds it\.$", pred47Action, "WISH SUCCESS")
standardPreds.append(t)

# 48
t = Pred("^Reshuffling the Black Market deck\.$", empty, "SHUFFLE BM")
standardPreds.append(t)

# 49
t = Pred("^(?P<player>.*) puts (?P<cards>.*) on the bottom of (.*)\.$", empty, "BOTTOMDECK")
standardPreds.append(t)

# 50
t = Pred("^(?P<cards>.*) loses track of (.*) \(it moved\)\.$", empty, "LOSETRACK MOVE")
standardPreds.append(t)

# 51
t = Pred("^(?P<cards>.*) loses track of (.*) \(it was covered up\)\.$", empty, "LOSETRACK COVER")
standardPreds.append(t)

# 52
t = Pred("^(?P<cards>.*) loses track of (.*) \(it was shuffled\)\.$", empty, "LOSETRACK SHUFFLE")
standardPreds.append(t)

# 53
t = Pred("^(?P<cards>.*) is lost track of\.$", empty, "LOSETRACK")
standardPreds.append(t)

# 54
t = Pred("^No differently named Action cards\.$", empty, "MUSEUM FAIL")
standardPreds.append(t)

# 55
t = Pred("^exactly one of (?P<player>.*)\.$", empty, "WOLFDEN")
standardPreds.append(t)

# 56
t = Pred("^(?P<player>.*) cards from the (?P<cards>.*)-pile\.$", empty, "OBELISK")
standardPreds.append(t)

# 57
t = Pred("^(?P<player>.*) differently named cards\.$", empty, "MUSEUM")
standardPreds.append(t)

# 58
t = Pred("^(?P<player>.*) Castles\.$", empty, "CASTLES")
standardPreds.append(t)

# 59
t = Pred("^(?P<player>.*) Action cards\.$", empty, "VINEYARDS")
standardPreds.append(t)

# 60
t = Pred("^(?P<player>.*) Victory cards\.$", empty, "SILK ROAD")
standardPreds.append(t)

# 61
t = Pred("^VP tokens\.$", empty, "SHIELDS")
standardPreds.append(t)


# 62
def pred62Action(move, i, bL, moves, cS):
    gS[-1].move(cM[0].player, 'OTHERS', 'HANDS', cM[0].items)


t = Pred("^(?P<player>.*) puts (?P<cards>.*) in hand \(Gear\)\.$", pred62Action, "DRAW GEAR")
standardPreds.append(t)


# 63
def pred63Action(move, i, bL, moves, cS):
    gS[-1].move(cM[0].player, 'OTHERS', 'HANDS', cM[0].items)


t = Pred("^(?P<player>.*) puts (?P<cards>.*) in hand \(Haven\)\.$", pred63Action, "DRAW HAVEN")
standardPreds.append(t)


# 64
def pred64Action(move, i, bL, moves, cS):
    gS[-1].move(cM[0].player, 'OTHERS', 'HANDS', cM[0].items)


t = Pred("^(?P<player>.*) puts (?P<cards>.*) in hand \(Archive\)\.$", pred64Action, "DRAW ARCHIVE")
standardPreds.append(t)


# 65
t = Pred("^(?P<player>.*) gets \+1 Action and \+1 Coin \(Fishing Village\)\.$", gainCash(1), "DURATION FV")
standardPreds.append(t)

# 66
t = Pred("^(?P<player>.*) gets \+2 Coins \(Merchant Ship\)\.$", gainCash(2), "DURATION MS")
standardPreds.append(t)

# 67
t = Pred("^(?P<player>.*) gets \+1 Coin \(Lighthouse\)\.$", gainCash(1), "DURATION LIGHTHOUSE")
standardPreds.append(t)

# 68
t = Pred("^(?P<player>.*) gets \+1 Coin \(Caravan Guard\)\.$", gainCash(1), "DURATION CGUARD")
standardPreds.append(t)

# 69
t = Pred("^(?P<player>.*) gets \+3 Coins \(Swamp Hag\)\.$", gainCash(3), "DURATION SHAG")
standardPreds.append(t)

# 70
t = Pred("^(?P<player>.*) summons (?P<cards>.*)\.$", empty, "SUMMON")
standardPreds.append(t)

# 71
t = Pred("^(?P<player>.*) gets \+1 Buy \(Bridge Troll\)\.$", empty, "DURATION TROLL")
standardPreds.append(t)


# 72
def turn_start_action(move, i, bL, moves, cS):
    exc.append(checkMove(['PLAY'], 'OTHERS', 'INPLAYS'))
    exc.append(Exception(check(['PLAY']), standardOnPlay))
    exc.append(checkMove(['PUT INHAND'], 'OTHERS', 'HANDS',
                                 ['Horse Traders']))

    # Probably Cobbler
    def immediate_gain_condition(cM):
        # Amulet!
        isSilver = cM[0].items.primary() == 'Silver'
        return str(move.pred) == 'GAIN' and cM[0].indent == 1 and not isSilver

    whichBoon = cM[0].items.primary()

    # Boons and Shit
    def add_stuff(move, i, bL, moves, cS):
        thisBoon = cM[0].items.primary()
        exc_gainNormally = Exception(check(['GAIN']),
                                     moveException('SUPPLY', 'DISCARDS'),
                                     priority=1)
        exc_onGainNormally = Exception(check(['GAIN']),
                                       standardOnGains('DISCARDS'),
                                       priority=1)

        def discardBoonhexCondition(cM):
            return cM[0].items.primary() == thisBoon and str(move.pred) == 'DISCARD'

        def remove_stuff(exceptions):
            def out_function(move, i, bL, moves, cS):
                for exception in exceptions:
                    if exception in tExc:
                        tExc.remove(exception)
            return out_function

        tExc.append(exc_gainNormally)
        tExc.append(exc_onGainNormally)
        tExc.append(Exception(discardBoonhexCondition,
                    remove_stuff([exc_gainNormally, exc_onGainNormally])))

    exc.append(Exception(check(['TAKES BOONHEX']), add_stuff))
    exc.append(Exception(immediate_gain_condition, moveException('SUPPLY', 'HANDS')))
    exc.append(Exception(immediate_gain_condition, standardOnGains('DECKS')))


t = Pred("^(?P<player>.*) starts their turn\.$", turn_start_action, "TURN START")
standardPreds.append(t)


# 73
def generic_vp_action(move, i, bL, moves, cS):
    gS[-1].vps[cM[0].player] += int(cM[0].items[ARGUMENT_CARD].split('/')[0])


t = Pred("^(?P<player>.*) takes (?P<cards>.*) VP from (.*)\.$", generic_vp_action, "SHIELD GAIN")
standardPreds.append(t)

# 74
t = Pred("^(?P<player>.*) moves (?P<cards>.*) VP from (.*) to (.*)\.$", empty, "SHIELD MOVE")
standardPreds.append(t)


# 75
def obelisk_choice(move, i, bL, moves, cS):
    target = cM[0].items
    gS[-1].obelisk = target
    for pair in pairs:
        if target in pair:
            gS[-1].obelisk = pair
            break


t = Pred("^Obelisk chooses (?P<cards>.*)\.$", obelisk_choice, "OBELISK CHOICE")
standardPreds.append(t)

# 76
t = Pred("^(?P<player>.*) moves (.*) to (.*)\.$", empty, "MOVE")
standardPreds.append(t)

# 77
t = Pred("^(?P<player>.*) gets (?P<cards>.*) VP\.$", generic_vp_action, "SHIELD GET")
standardPreds.append(t)

# 78
t = Pred("^(?P<player>.*) gets (?P<cards>.*) VP from Groundskeeper\.$", generic_vp_action, "SHIELD GROUNDSKEEPER")
standardPreds.append(t)

# 79
t = Pred("^(?P<player>.*) gets (?P<cards>.*) VP from Goons\.$", generic_vp_action, "SHIELD GOONS")
standardPreds.append(t)

# 80
t = Pred("^(?P<player>.*) gets (?P<cards>.*) VP from (.*)\.$", generic_vp_action, "SHIELD OTHER")
standardPreds.append(t)

# 81
t = Pred("^(?P<player>.*) adds (?P<cards>.*) VP to (.*)\.$", empty, "SHIELD ADD")
standardPreds.append(t)

# 82
t = Pred("^Waiting for (?P<player>.*)\.$", empty, "WAITING")
standardPreds.append(t)

# 83
t = Pred("^(?P<player>.*) failed to discard an Attack\.$", empty, "QUEST ATTACKFAIL")
standardPreds.append(t)

# 84
t = Pred("^(?P<player>.*) failed to discard 6 cards\.$", empty, "QUEST CARDFAIL")
standardPreds.append(t)

# 85
t = Pred("^(?P<player>.*) failed to discard (?P<cards>.*)\.$", empty, "DISCARD FAIL")
standardPreds.append(t)

# 86
t = Pred("^(?P<player>.*) had no cards to set aside\.$", empty, "SET FAIL")
standardPreds.append(t)

# 87
t = Pred("^(?P<player>.*) had no cards to discard or topdeck\.$", empty, "TOPDECK FAIL")
standardPreds.append(t)

# 88
t = Pred("^Mission fails because (?P<player>.*) already owned the previous turn\.$", empty, "MISSION FAIL")
standardPreds.append(t)

# 89
t = Pred("^(?P<player>.*) takes an extra turn after this one\.$", empty, "EXTRATURN")
standardPreds.append(t)

# 90
t = Pred("^(?P<player>.*) flips (.*) face down\.$", empty, "FLIP DOWN")
standardPreds.append(t)

# 91
t = Pred("^(?P<player>.*) flips (.*) face up\.$", empty, "FLIP UP")
standardPreds.append(t)

# 92
t = Pred("^(?P<player>.*) failed to gain (?P<cards>.*)\.$", empty, "GAIN FAIL")
standardPreds.append(t)

# 93
t = Pred("^(?P<player>.*) didn't trash an Action card\.$", empty, "ACTIONTRASH FAIL")
standardPreds.append(t)

# 94
t = Pred("^(?P<player>.*) adds (?P<cards>.*) to (.*)\.$", empty, "ADD TO")
standardPreds.append(t)

# 95
t = Pred("^(?P<player>.*) takes (?P<cards>.*) from (.*)\.$", empty, "TAKE FROM")
standardPreds.append(t)

# 96
t = Pred("^(?P<player>.*) isn't empty\.$", empty, "NOT EMPTY")
standardPreds.append(t)

# 97
t = Pred("^(?P<player>.*) gets \+1 Action \(from (?P<cards>.*)\)$", empty, "ACTION TOKEN")
standardPreds.append(t)

# 98
t = Pred("^(?P<player>.*) gets \+1 Buy \(from (?P<cards>.*)\)$", empty, "BUY TOKEN")
standardPreds.append(t)

# 99
t = Pred("^(?P<player>.*) gets \+1 Coin \(from (?P<cards>.*)\)$", empty, "COIN TOKEN")
standardPreds.append(t)

# 100
t = Pred("^(?P<player>.*) skips a draw \(because of (?P<cards>.*)\)$", empty, "PENALTY CARD")
standardPreds.append(t)

# 101
t = Pred("^(?P<player>.*) takes the coin tokens instead\.$", empty, "TAKE CHIPS")
standardPreds.append(t)

# 102
t = Pred("^(?P<player>.*) takes the Debt instead\.$", empty, "TAKE DEBT INSTEAD")
standardPreds.append(t)

# 103
t = Pred("^(?P<player>.*) takes the VP tokens instead\.$", empty, "TAKE SHIELD")
standardPreds.append(t)

# 104
t = Pred("^Outpost fails because (?P<player>.*) already owned the previous turn\.$", empty, "OUTPOST FAIL")
standardPreds.append(t)

# 105
t = Pred("^Outpost fails because (?P<player>.*) has already played it\.$", empty, "OUTPOST FAIL2")
standardPreds.append(t)

# 106
t = Pred("^(?P<player>.*) takes (?P<cards>.*) debt\.$", empty, "TAKE DEBT")
standardPreds.append(t)

# 107
t = Pred("^(?P<player>.*) repays (?P<cards>.*)\.$", empty, "REPAY DEBT")
standardPreds.append(t)

# 108
t = Pred("^(?P<player>.*) repays (?P<cards>.*) \((.*) remaining\)\.$", empty, "REPAY DEBT PARTIAL")
standardPreds.append(t)


# 109
def setAsideWith_action(move, i, bL, moves, cS):
    standardMove('HANDS', 'OTHERS', cM, gS)


t = Pred("^(?P<player>.*) sets (?P<cards>.*) aside with (.*)\.$", setAsideWith_action, "SET ASIDE WITH")
standardPreds.append(t)

# 110
t = Pred("^(?P<player>.*) blocks with (?P<cards>.*)\.$", empty, "BLOCK")
standardPreds.append(t)

# 111
t = Pred("^(?P<player>.*) names (?P<cards>.*)\.$", empty, "NAME")
standardPreds.append(t)

# 112
t = Pred("^Obelisk failed to select an Action Supply pile\.$", empty, "OBELISK FAIL")
standardPreds.append(t)


# 113
def pred113Action(move, i, bL, moves, cS):
    gS[-1].move(cM[0].player, 'SUPPLY', 'OTHERS', cM[0].items)
    gS[-1].INHERITED_CARDS[cM[0].player] = cM[0].items.cardList()[0]


t = Pred("^(?P<player>.*) inherits (?P<cards>.*)\.$", pred113Action, "INHERIT")
standardPreds.append(t)

# 114
t = Pred("^(?P<player>.*) fails to discard for The Sky's Gift$", empty, "SKY GIFT FAIL")
standardPreds.append(t)

# 115
def predCryptAction(move, i, bL, moves, cS):
    gS[-1].move(cM[0].player, 'OTHERS', 'HANDS', cM[0].items)

t = Pred("^(?P<player>.*) puts (?P<cards>.*) in hand \(Crypt\)\.$", predCryptAction, "CRYPT")
standardPreds.append(t)

# 116
t = Pred("^(?P<player>.*) gets \+1 Coin \(Guardian\)\.$", empty, "DURATION GUARDIAN")
standardPreds.append(t)


# 117
t = Pred("^(?P<player>.*) takes (?P<cards>.*)\.$", empty, "TAKES BOONHEX")
standardPreds.append(t)

# 118
t = Pred("^The Sun's Gift has nothing to discard\.$", empty, "SUN GIFT FAIL")
standardPreds.append(t)

# 119
t = Pred("^Druid sets (?P<cards>.*) aside\.$", empty, "DRUID BOONS")
standardPreds.append(t)

# 120
t = Pred("^(?P<player>.*) gets \+3 Coins \(Raider\)\.$", empty, "DURATION RAIDER")
standardPreds.append(t)

# 121
t = Pred("^(?P<player>.*) gets \+3 Coins \(Secret Cave\)\.$", empty, "DURATION CAVE")
standardPreds.append(t)

# 122
t = Pred("^(?P<cards>.*) is enchanted by (.*)$", empty, "ENCHANTED")
standardPreds.append(t)

# 123
def predDonateAction(move, i, bL, moves, cS):
    def moveEverything(move, i, bL, moves, cS):
        gS[-1].move(cM[0].player, 'DECKS', 'HANDS',
                            gS[-1].DECKS[cM[0].player])
        gS[-1].move(cM[0].player, 'DISCARDS', 'HANDS',
                            gS[-1].DISCARDS[cM[0].player])

    def shuffleBack(move, i, bL, moves, cS):
        gS[-1].move(cM[0].player, 'HANDS', 'DECKS',
                            gS[-1].HANDS[cM[0].player])

    exc.append(Exception(check(['PUT INHAND']), moveEverything))
    exc.append(Exception(check(['SHUFFLE INTO']), shuffleBack))


t = Pred("^Between Turns$", predDonateAction, "BETWEEN TURNS")
standardPreds.append(t)

# Last - catchall
t = Pred("^(.*)$", empty, "OTHERS")
standardPreds.append(t)


def urchin_trash_condition(cM):
    out = 0
    for index in range(1, len(cM)-1):
        if check(['TRASH'], ['Urchin'])(cM[index]) and out == 0:
            out = 1

        if check(['GAIN'], ['Mercenary'])(cM[index + 1]) and out == 1:
            out = 2
    return out == 2


def urchin_trash_exception(move, i, bL, moves, cS):
    standardPreds[cM[0].pred].action(cM, gS, exc, tExc, pers)
    standardOnPlay(cM, gS, exc, tExc, pers)

    exc.append(Exception(check(['TRASH'], ['Urchin']),
                         moveException('INPLAYS', 'TRASH'),
                         priority=1))


def hermit_trash_condition(cM):
    out = 0
    for index in range(1, len(cM)-1):
        if check(['TRASH'], ['Hermit'])(cM[index]) and out == 0:
            out = 1

        if check(['GAIN'], ['Madman'])(cM[index + 1]) and out == 1:
            out = 2
    return out == 2


def hermit_trash_exception(move, i, bL, moves, cS):
    standardPreds[cM[0].pred].action(cM, gS, exc, tExc, pers)
    standardOnPlay(cM, gS, exc, tExc, pers)

    exc.append(Exception(check(['TRASH'], ['Hermit']),
                         moveException('INPLAYS', 'TRASH'),
                         priority=1))


standardPersistents.append(Exception(urchin_trash_condition, urchin_trash_exception))
standardPersistents.append(Exception(hermit_trash_condition, hermit_trash_exception))
standardPersistents.append(checkMove(['RETURN TO'], 'OTHERS', 'SUPPLY',
                                             ['Encampment']))
travellers = ['Page', 'Treasure Hunter', 'Warrior', 'Hero', 'Champion', 'Peasant', 'Soldier', 'Fugitive', 'Disciple', 'Teacher']
standardPersistents.append(checkMove(['RETURN'], 'INPLAYS', 'SUPPLY',
                                             travellers))
standardPersistents.append(Exception(check(['DISCARD'], ['Wine Merchant']),
                                     moveException('OTHERS', 'DISCARDS')))

standardNames = [x.simple_name for x in standardCards]
