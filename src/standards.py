from .classes import *
from .lists import *
from copy import deepcopy


def empty(cM, gS, exc, tExc, pers):
    pass


def standardCondition(predList, targetList=[]):
    def out_function(cM):
        if predList:
            if standardPreds[cM[0].pred].name not in predList:
                return False
        if targetList:
            inside = False
            for card in targetList:
                if standardNames.index(card) in cM[0].items:
                    inside = True
            if not inside:
                return False
        return True

    return out_function


def moveException(src, dest):
    def out_function(cM, gS, exc, tExc, pers):
        standardMove(src, dest, cM, gS)
    return out_function


def standardMove(src, dest, cM, gS):
    if cM[0].items.count() > 0:
        gS[-1].move(cM[0].player, src, dest, cM[0].items)


def standardException(predList, src, dest, targetList=[]):
    return Exception(standardCondition(predList, targetList),
                     moveException(src, dest))


def gainCash(amount):
    def out_function(cM, gS, exc, tExc, pers):
        player = cM[0].player
        gS[-1].coins[player] += amount

    return out_function


def standardOnGains(src):
    def specificCondition(predList, gainedCard):
        def out_function(cM):
            if standardPreds[cM[0].pred].name not in predList:
                return False
            return (cM[0].items - gainedCard).count() == 0 or\
                cM[0].items.primary() == 'card'
        return out_function

    def villaException(cM, gS, exc, tExc, pers):
        moveException(src, 'HANDS')(cM, gS, exc, tExc, pers)
        gS[-1].phase = 0

    def out_function(cM, gS, exc, tExc, pers):
        if cM[0].predName() in ['GAIN', 'BUY AND GAIN', 'GAIN TOPDECK', 'GAIN TRASH']:
            gainedCard = cM[0].items
        else:
            for subchunk in cM[1:]:
                if subchunk[0].predName() in ['GAIN', 'BUY AND GAIN', 'GAIN TOPDECK', 'GAIN TRASH']:
                    gainedCard = subchunk[0].items

        def topdeckerMove(cM, gS, exc, tExc, pers):
            gS[-1].move(cM[0].player, src, 'DECKS', gainedCard)

        def trasherMove(cM, gS, exc, tExc, pers):
            gS[-1].move(cM[0].player, src, 'TRASH', gainedCard)

        def returnMove(cM, gS, exc, tExc, pers):
            gS[-1].move(cM[0].player, src, 'SUPPLY', gainedCard)

        exc.append(Exception(specificCondition(['TOPDECK'], gainedCard),
                             topdeckerMove))
        exc.append(Exception(specificCondition(['TRASH'], gainedCard),
                             trasherMove))
        exc.append(Exception(specificCondition(['RETURN'], gainedCard),
                             returnMove))
        if gainedCard.primary() == 'Villa':
            exc.append(Exception(standardCondition(['PUT INHAND'], ['Villa']),
                                 villaException))

    return out_function


def standardOnPlay(cM, gS, exc, tExc, pers):
    for card in cM[0].items:
        if card != ARGUMENT_CARD:
            for i in range(cM[0].items[card]):
                standardCards[card].action(cM, gS, exc, tExc, pers)


def standardOnTrash(cM, gS, exc, tExc, pers):
    for card in cM[0].items:
        if card != ARGUMENT_CARD:
            for i in range(cM[0].items[card]):
                standardCards[card].action(cM, gS, exc, tExc, pers)


def staticWorth(val):
    def out_function(gS, player):
        return val
    return out_function


def knightsTrashCondition(knightPlayer):
    def out_function(cM):
        return cM[0].predName() == 'TRASH' and cM[0].player != knightPlayer
    return out_function


exc_revealTrash = standardException(['TRASH'], 'DECKS', 'TRASH')
exc_revealTopdeck = standardException(['TOPDECK'], 'DECKS', 'DECKS')
exc_revealDiscard = standardException(['DISCARD'], 'DECKS', 'DISCARDS')
exc_harbinger = standardException(['TOPDECK'], 'DISCARDS', 'DECKS')
exc_gainHand = standardException(['GAIN'], 'SUPPLY', 'HANDS')
exc_supplyTrash = standardException(['TRASH'], 'SUPPLY', 'TRASH')
exc_inplayTrash = standardException(['TRASH'], 'INPLAYS', 'TRASH')
exc_standardTrash = Exception(standardCondition(['TRASH']), standardOnTrash)

# First: Argument
t = Card('Argument', 'Argument', 'Argument', 0, 0, '666666', '666666', empty)
standardCards.append(t)

# 0: nothing
t = Card('nothing', 'other cards', 'nothing', 0, -1, '666666', '666666', empty)
standardCards.append(t)

# 1: card
t = Card('card', 'cards', 'a card', 0, -1, '666666', '1528B7', empty)
standardCards.append(t)

# 2: Curse
t = Card('Curse', 'Curses', 'a Curse', 0, -1, 'b571b3', 'a2b8b8', empty, staticWorth(-1))
standardCards.append(t)


# 3: Copper
def copper_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(1)(cM, gS, exc, tExc, pers)


t = Card('Copper', 'Coppers', 'a Copper', 0, -1, 'f1d14d', 'a05624', copper_action)
standardCards.append(t)


# 4: Silver
def silver_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(2)(cM, gS, exc, tExc, pers)


t = Card('Silver', 'Silvers', 'a Silver', 3, -1, 'f1d14d', '709aa4', silver_action)
standardCards.append(t)


# 5: Gold
def gold_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(3)(cM, gS, exc, tExc, pers)


t = Card('Gold', 'Golds', 'a Gold', 6, -1, 'f1d14d', 'ffae06', gold_action)
standardCards.append(t)


# 6: Estate
def estate_action(cM, gS, exc, tExc, pers):
    card = standardCards[gS[-1].INHERITED_CARDS[cM[0].player]]
    card.action(cM, gS, exc, tExc, pers)


t = Card('Estate', 'Estates', 'an Estate', 2, -1, '548C2B', 'bfb597', estate_action, staticWorth(1))
standardCards.append(t)

# 7: Duchy
t = Card('Duchy', 'Duchies', 'a Duchy', 5, -1, '548C2B', '6aa09a', empty, staticWorth(3))
standardCards.append(t)

# 8: Province
t = Card('Province', 'Provinces', 'a Province', 8, -1, '548C2B', 'efaf49', empty, staticWorth(6))
standardCards.append(t)


# 9: Artisan
def artisan_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_gainHand)
        exc.append(Exception(standardCondition(['GAIN']),
                             standardOnGains('HANDS')))


t = Card('Artisan', 'Artisans', 'an Artisan', 6, 0, 'c4c0b4', 'bc5a00', artisan_action)
standardCards.append(t)


# 10: Bandit
def bandit_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealTrash)
        exc.append(exc_standardTrash)
        exc.append(exc_revealDiscard)


t = Card('Bandit', 'Bandits', 'a Bandit', 5, 0, 'c4c0b4', '8a861e', bandit_action)
standardCards.append(t)


# 11: Bureaucrat
def bureaucrat_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['GAIN'], 'SUPPLY', 'DECKS', ['Silver']))
        exc.append(Exception(standardCondition(['GAIN']),
                             standardOnGains('DECKS')))


t = Card('Bureaucrat', 'Bureaucrats', 'a Bureaucrat', 4, 0, 'c4c0b4', '95633b', bureaucrat_action)
standardCards.append(t)

# 12: Cellar
t = Card('Cellar', 'Cellars', 'a Cellar', 2, 0, 'c4c0b4', '3e4646', empty)
standardCards.append(t)

# 13: Chapel
t = Card('Chapel', 'Chapels', 'a Chapel', 2, 0, 'c4c0b4', '605444', empty)
standardCards.append(t)

# 14: Council Room
t = Card('Council Room', 'Council Rooms', 'a Council Room', 5, 0, 'c4c0b4', '815121', empty)
standardCards.append(t)


# 15: Festival
def festival_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(2)(cM, gS, exc, tExc, pers)


t = Card('Festival', 'Festivals', 'a Festival', 5, 0, 'c4c0b4', '636d61', festival_action)
standardCards.append(t)


# 16: Gardens
def gardens_worth(gameState, player):
    return gameState.crunch(['DECKS', 'HANDS', 'DISCARDS', 'OTHERS',
                             'INPLAYS'], [player]).count()//10


t = Card('Gardens', 'Gardens', 'a Gardens', 4, 0, '9cbe8a', '5f792f', empty, gardens_worth)
standardCards.append(t)


# 17: Harbinger
def harbinger_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_harbinger)


t = Card('Harbinger', 'Harbingers', 'a Harbinger', 3, 0, 'c4c0b4', '8e8a3c', harbinger_action)
standardCards.append(t)


# 18: Laboratory
t = Card('Laboratory', 'Laboratories', 'a Laboratory', 5, 0, 'c4c0b4', '614739', empty)
standardCards.append(t)


# 19: Library
def library_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['SETS ASIDE WITH'], 'DECKS', 'OTHERS'))
        exc.append(standardException(['DISCARD'], 'OTHERS', 'DISCARDS'))


t = Card('Library', 'Libraries', 'a Library', 5, 0, 'c4c0b4', '7a7e4a', library_action)
standardCards.append(t)


# 20: Market
def market_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(1)(cM, gS, exc, tExc, pers)


t = Card('Market', 'Markets', 'a Market', 5, 0, 'c4c0b4', '684830', market_action)
standardCards.append(t)


# 21: Merchant
t = Card('Merchant', 'Merchants', 'a Merchant', 3, 0, 'c4c0b4', '917911', empty)
standardCards.append(t)


# 22: Militia
def militia_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(2)(cM, gS, exc, tExc, pers)

t = Card('Militia', 'Militias', 'a Militia', 4, 0, 'c4c0b4', '856961', militia_action)
standardCards.append(t)


# 23: Mine
def mine_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_gainHand)
        exc.append(Exception(standardCondition(['GAIN']),
                             standardOnGains('HANDS')))


t = Card('Mine', 'Mines', 'a Mine', 5, 0, 'c4c0b4', '433935', mine_action)
standardCards.append(t)

# 24: Moat
t = Card('Moat', 'Moats', 'a Moat', 2, 0, '8ca2be', '586472', empty)
standardCards.append(t)


# 25: Moneylender
t = Card('Moneylender', 'Moneylenders', 'a Moneylender', 4, 0, 'c4c0b4', '7a644c', empty)
standardCards.append(t)


# 26: Poacher
def poacher_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(1)(cM, gS, exc, tExc, pers)

t = Card('Poacher', 'Poachers', 'a Poacher', 4, 0, 'c4c0b4', '8f810d', poacher_action)
standardCards.append(t)

# 27: Remodel
t = Card('Remodel', 'Remodels', 'a Remodel', 4, 0, 'c4c0b4', '8e7e4a', empty)
standardCards.append(t)


# 28: Sentry
def sentry_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealTrash)
        exc.append(exc_standardTrash)
        exc.append(exc_revealDiscard)
        exc.append(exc_revealTopdeck)


t = Card('Sentry', 'Sentries', 'a Sentry', 5, 0, 'c4c0b4', '5a361e', sentry_action)
standardCards.append(t)

# 29: Smithy
t = Card('Smithy', 'Smithies', 'a Smithy', 4, 0, 'c4c0b4', '6a523a', empty)
standardCards.append(t)

# 30: Throne Room
t = Card('Throne Room', 'Throne Rooms', 'a Throne Room', 4, 0, 'c4c0b4', 'd76315', empty)
standardCards.append(t)


# 31: Vassal
def vassal_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(2)(cM, gS, exc, tExc, pers)

        exc.append(exc_revealDiscard)
        discardedCard = standardCards[CARD_CARD].simple_name
        for subchunk in cM[1:]:
            if subchunk[0].predName() == 'DISCARD':
                discardedCard = subchunk[0].items.primary()
                break

        # You're fucked up, vassal.
        tExc.append(Exception(standardCondition(['PLAY'], [discardedCard]),
                              moveException('DISCARDS', 'INPLAYS'), len(cM)))
        tExc.append(Exception(standardCondition(['PLAY'], [discardedCard]),
                              standardOnPlay, len(cM)))


t = Card('Vassal', 'Vassals', 'a Vassal', 3, 0, 'c4c0b4', 'ba6816', vassal_action)
standardCards.append(t)

# 32: Village
t = Card('Village', 'Villages', 'a Village', 3, 0, 'c4c0b4', '7e9078', empty)
standardCards.append(t)

# 33: Witch
t = Card('Witch', 'Witches', 'a Witch', 5, 0, 'c4c0b4', '52444e', empty)
standardCards.append(t)

# 34: Workshop
t = Card('Workshop', 'Workshops', 'a Workshop', 3, 0, 'c4c0b4', '8c6428', empty)
standardCards.append(t)

# 35: Courtyard
t = Card('Courtyard', 'Courtyards', 'a Courtyard', 2, 0, 'c4c0b4', '74a454', empty)
standardCards.append(t)


# 36: Conspirator
def conspirator_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(2)(cM, gS, exc, tExc, pers)


t = Card('Conspirator', 'Conspirators', 'a Conspirator', 4, 0, 'c4c0b4', '2b5989', conspirator_action)
standardCards.append(t)

# 37: Courtier
t = Card('Courtier', 'Courtiers', 'a Courtier', 5, 0, 'c4c0b4', 'ac6228', empty)
standardCards.append(t)

# 38: Baron
t = Card('Baron', 'Barons', 'a Baron', 4, 0, 'c4c0b4', '876341', empty)
standardCards.append(t)


# 39: Bridge
def bridge_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(1)(cM, gS, exc, tExc, pers)


t = Card('Bridge', 'Bridges', 'a Bridge', 4, 0, 'c4c0b4', '859b6b', bridge_action)
standardCards.append(t)


# 40: Diplomat
def diplomat_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['REACT']:
        newExc = standardException(['DISCARD'], 'HANDS', 'DISCARDS')
        newExc.priority = 2
        tExc.append(newExc)


t = Card('Diplomat', 'Diplomats', 'a Diplomat', 4, 0, '8ca2be', '91595f', diplomat_action)
standardCards.append(t)


# 41: Duke
def duke_worth(gS, player):
    playerDeck = gS.crunch(['DECKS', 'HANDS', 'DISCARDS', 'OTHERS'],
                           [player])

    for card in playerDeck:
        if standardCards[card].simple_name == 'Duchy':
            return playerDeck[card]
    return 0


t = Card('Duke', 'Dukes', 'a Duke', 5, 0, '9cbe8a', '8a7e5e', empty, duke_worth)
standardCards.append(t)


# 42: Harem
t = Card('Harem', 'Harems', 'a Harem', 6, 0, 'a9c35d', 'c3510d', empty, staticWorth(2))
standardCards.append(t)


# 43: Nobles
t = Card('Nobles', 'Nobles', 'a Nobles', 6, 0, 'aac298', '816155', empty, staticWorth(2))
standardCards.append(t)


# 44: Ironworks
t = Card('Ironworks', 'Ironworks', 'an Ironworks', 4, 0, 'c4c0b4', '7d3b1f', empty)
standardCards.append(t)


# 45: Lurker
def lurker_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_supplyTrash)
        exc.append(exc_standardTrash)
        exc.append(standardException(['GAIN'], 'TRASH', 'DISCARDS'))
        exc.append(Exception(standardCondition(['GAIN']),
                             standardOnGains('DECKS')))


t = Card('Lurker', 'Lurkers', 'a Lurker', 2, 0, 'c4c0b4', '909ab2', lurker_action)
standardCards.append(t)


# 46: Masquerade
t = Card('Masquerade', 'Masquerades', 'a Masquerade', 3, 0, 'c4c0b4', '635d51', empty)
standardCards.append(t)

# 47: Mill
t = Card('Mill', 'Mills', 'a Mill', 4, 0, 'aac298', '78b294', empty, staticWorth(1))
standardCards.append(t)

# 48: Mining Village
def minevillage_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_inplayTrash)
        exc.append(exc_standardTrash)

t = Card('Mining Village', 'Mining Villages', 'a Mining Village', 4, 0, 'c4c0b4', 'aea090', minevillage_action)
standardCards.append(t)

# 49: Minion
def minion_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        for chunk in cM[1:]:
            if standardPreds[chunk[0].pred].name != 'DISCARD':
                gainCash(2)(cM, gS, exc, tExc, pers)

t = Card('Minion', 'Minions', 'a Minion', 5, 0, 'c4c0b4', '6c382e', minion_action)
standardCards.append(t)

# 50: Patrol
def patrol_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealTopdeck)

t = Card('Patrol', 'Patrols', 'a Patrol', 5, 0, 'c4c0b4', '98ae70', patrol_action)
standardCards.append(t)

# 51: Pawn
t = Card('Pawn', 'Pawns', 'a Pawn', 2, 0, 'c4c0b4', '3f2f25', empty)
standardCards.append(t)


# 52: Replace
def replace_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainedCard = CARD_CARD
        for subchunk in cM[1:]:
            if subchunk[0].predName() == 'GAIN' and \
               subchunk[0].player == cM[0].player:
                gainedCard = subchunk[0].items.cardList()[0]
        gainedCardStack = Cardstack({gainedCard: 1})

        def topdeckGainedCard(cM, gS, exc, tExc, pers):
            gS[-1].move(cM[0].player, 'DISCARDS', 'DECKS', gainedCardStack)

        exc.append(Exception(standardCondition(['TOPDECK']), topdeckGainedCard))


t = Card('Replace', 'Replaces', 'a Replace', 5, 0, 'c4c0b4', '564850', replace_action)
standardCards.append(t)

# 53: Secret Passage
t = Card('Secret Passage', 'Secret Passages', 'a Secret Passage', 4, 0, 'c4c0b4', '261e12', empty)
standardCards.append(t)

# 54: Shanty Town
t = Card('Shanty Town', 'Shanty Towns', 'a Shanty Town', 3, 0, 'c4c0b4', '124e44', empty)
standardCards.append(t)

# 55: Steward
t = Card('Steward', 'Stewards', 'a Steward', 3, 0, 'c4c0b4', '4f4d5d', empty)
standardCards.append(t)

# 56: Swindler
def swindler_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealTrash)
        exc.append(exc_standardTrash)


t = Card('Swindler', 'Swindlers', 'a Swindler', 3, 0, 'c4c0b4', 'b78d49', swindler_action)
standardCards.append(t)

# 57: Torturer
def torturer_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['GAIN'], 'SUPPLY', 'HANDS', ['Curse']))
        exc.append(Exception(standardCondition(['GAIN'], ['Curse']),
                             standardOnGains('HANDS')))

t = Card('Torturer', 'Torturers', 'a Torturer', 5, 0, 'c4c0b4', '842804', torturer_action)
standardCards.append(t)

# 58: Trading Post
def tradepost_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['GAIN'], 'SUPPLY', 'HANDS', ['Silver']))
        exc.append(Exception(standardCondition(['GAIN'], ['Silver']),
                             standardOnGains('HANDS')))

t = Card('Trading Post', 'Trading Posts', 'a Trading Post', 5, 0, 'c4c0b4', '686434', tradepost_action)
standardCards.append(t)

# 59: Upgrade
t = Card('Upgrade', 'Upgrades', 'an Upgrade', 5, 0, 'c4c0b4', '979773', empty)
standardCards.append(t)

# 60: Wishing Well
t = Card('Wishing Well', 'Wishing Wells', 'a Wishing Well', 3, 0, 'c4c0b4', '61756b', empty)
standardCards.append(t)


# 61: Ambassador
def ambassador_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['RETURN TO'], 'HANDS', 'SUPPLY'))


t = Card('Ambassador', 'Ambassadors', 'an Ambassador', 3, 0, 'c4c0b4', 'b8602c', ambassador_action)
standardCards.append(t)


# 62: Bazaar
def bazaar_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(1)(cM, gS, exc, tExc, pers)


t = Card('Bazaar', 'Bazaars', 'a Bazaar', 5, 0, 'c4c0b4', 'a6765e', bazaar_action)
standardCards.append(t)

# 63: Caravan
t = Card('Caravan', 'Caravans', 'a Caravan', 4, 0, 'dda561', 'b9ab7f', empty)
standardCards.append(t)


# 64: Cutpurse
def cutpurse_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(2)(cM, gS, exc, tExc, pers)


t = Card('Cutpurse', 'Cutpurses', 'a Cutpurse', 4, 0, 'c4c0b4', '826a4e', cutpurse_action)
standardCards.append(t)


# 65: Embargo
def embargo_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(2)(cM, gS, exc, tExc, pers)
        exc.append(exc_inplayTrash)
        exc.append(exc_standardTrash)


t = Card('Embargo', 'Embargos', 'an Embargo', 2, 0, 'c4c0b4', '9da381', embargo_action)
standardCards.append(t)


# 66: Explorer
def explorer_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['GAIN'], 'SUPPLY', 'HANDS',
                                     ['Silver', 'Gold']))
        exc.append(Exception(standardCondition(['GAIN'], ['Silver', 'Gold']),
                             standardOnGains('HANDS')))


t = Card('Explorer', 'Explorers', 'an Explorer', 5, 0, 'c4c0b4', '74D0F6', explorer_action)
standardCards.append(t)


# 67: Fishing Village
def fishvillage_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(1)(cM, gS, exc, tExc, pers)

t = Card('Fishing Village', 'Fishing Villages', 'a Fishing Village', 3, 0, 'dda561', '7db9b3', fishvillage_action)
standardCards.append(t)

# 68: Ghost Ship
t = Card('Ghost Ship', 'Ghost Ships', 'a Ghost Ship', 5, 0, 'c4c0b4', '59814d', empty)
standardCards.append(t)

# 69: Haven
t = Card('Haven', 'Havens', 'a Haven', 2, 0, 'dda561', '866846', empty)
standardCards.append(t)


# 70: Island
def island_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        islandID = standardNames.index('Island')
        islandStack = Cardstack({islandID: 1})
        otherStuff = cM[0].items - islandStack

        def islandSetaside(islandStack, otherStuff):
            def out_function(cM, gS, exc, tExc, pers):
                gS[-1].move(cM[0].player, 'INPLAYS', 'OTHERS', islandStack)
                gS[-1].move(cM[0].player, 'HANDS', 'OTHERS', otherStuff)
            return out_function

        exc.append(Exception(standardCondition(['PUT ONTO']),
                                    islandSetaside(islandStack, otherStuff)))


t = Card('Island', 'Islands', 'an Island', 4, 0, 'aac298', '5d9fbd', island_action, staticWorth(2))
standardCards.append(t)


# 71: Lighthouse
def lighthouse_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(1)(cM, gS, exc, tExc, pers)


t = Card('Lighthouse', 'Lighthouses', 'a Lighthouse', 2, 0, 'dda561', '559773', lighthouse_action)
standardCards.append(t)


# 72: Lookout
def lookout_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealTrash)
        exc.append(exc_standardTrash)
        exc.append(exc_revealDiscard)
        exc.append(exc_revealTopdeck)


t = Card('Lookout', 'Lookouts', 'a Lookout', 3, 0, 'c4c0b4', '723a6a', lookout_action)
standardCards.append(t)


# 73: Merchant Ship
def merchship_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(2)(cM, gS, exc, tExc, pers)


t = Card('Merchant Ship', 'Merchant Ships', 'a Merchant Ship', 5, 0, 'dda561', 'b58127', merchship_action)
standardCards.append(t)


# 74: Native Village
def nv_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['PUT INHAND'], 'OTHERS', 'HANDS'))
        exc.append(standardException(['SET ASIDE WITH'], 'DECKS', 'OTHERS'))


t = Card('Native Village', 'Native Villages', 'a Native Village', 2, 0, 'c4c0b4', '6f919f', nv_action)
standardCards.append(t)


# 75: Navigator
def navigator_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(2)(cM, gS, exc, tExc, pers)
        exc.append(exc_revealTopdeck)
        exc.append(exc_revealDiscard)


t = Card('Navigator', 'Navigators', 'a Navigator', 4, 0, 'c4c0b4', '5ba7ad', navigator_action)
standardCards.append(t)


# 76: Outpost
t = Card('Outpost', 'Outposts', 'an Outpost', 5, 0, 'dda561', '949ab2', empty)
standardCards.append(t)


# 77: Pearl Diver
def pearldiver_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['TOPDECK'], 'DECKS', 'DECKS'))


t = Card('Pearl Diver', 'Pearl Divers', 'a Pearl Diver', 2, 0, 'c4c0b4', '00aee6', pearldiver_action)
standardCards.append(t)


# 78: Pirate Ship
def generalized_pirateship(value):
    def pirateship_action(cM, gS, exc, tExc, pers):
        if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
            exc.append(exc_revealTrash)
            exc.append(exc_revealDiscard)
            exc.append(exc_standardTrash)
            gainCash(value)(cM, gS, exc, tExc, pers)

            for chunk in cM[1:]:
                if chunk[0].predName == 'REVEAL':
                    gainCash(-value)(cM, gS, exc, tExc, pers)

                if chunk[0].predName == 'TRASH':
                    pers.append(Exception(
                        standardCondition(['PLAY', 'PLAY AGAIN', 'PLAY THIRD'],
                                          ['Pirate Ship']),
                        generalized_pirateship(value + 1))
                    )

    return pirateship_action


t = Card('Pirate Ship', 'Pirate Ships', 'a Pirate Ship', 4, 0, 'c4c0b4', '7e9ec2', generalized_pirateship(0))
standardCards.append(t)


# 79: Salvager
t = Card('Salvager', 'Salvagers', 'a Salvager', 4, 0, 'c4c0b4', '397b7b', empty)
standardCards.append(t)


# 80: Sea Hag
def seahag_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealDiscard)
        exc.append(standardException(['GAIN'], 'SUPPLY', 'DECKS', ['Curse']))
        exc.append(Exception(standardCondition(['GAIN']),
                             standardOnGains('DECKS')))


t = Card('Sea Hag', 'Sea Hags', 'a Sea Hag', 4, 0, 'c4c0b4', '745a44', seahag_action)
standardCards.append(t)

# 81: Smugglers
t = Card('Smugglers', 'Smugglers', 'a Smugglers', 3, 0, 'c4c0b4', '464c50', empty)
standardCards.append(t)

# 82: Tactician
t = Card('Tactician', 'Tacticians', 'a Tactician', 5, 0, 'dda561', '785c44', empty)
standardCards.append(t)


# 83: Treasure Map
def tmap_action(cM, gS, exc, tExc, pers):
    def tmap_one_tmap(cM):
        if cM[0].predName() == 'TRASH':
            if cM[0].items.primary() == 'Treasure Map':
                if cM[0].items[standardNames.index('Treasure Map')] == 1:
                    return True
        return False

    def tmap_two_tmap(cM):
        if cM[0].predName() == 'TRASH':
            if cM[0].items.primary() == 'Treasure Map':
                if cM[0].items[standardNames.index('Treasure Map')] == 2:
                    return True
        return False

    def tmap_double_trash(cM, gS, exc, tExc, pers):
        single_map = Cardstack({standardNames.index('Treasure Map'): 1})
        gS[-1].move(cM[0].player, 'INPLAYS', 'TRASH', single_map)
        gS[-1].move(cM[0].player, 'HANDS', 'TRASH', single_map)

    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(Exception(tmap_one_tmap, moveException('INPLAYS', 'TRASH')))
        exc.append(Exception(tmap_two_tmap, tmap_double_trash))


t = Card('Treasure Map', 'Treasure Maps', 'a Treasure Map', 4, 0, 'c4c0b4', '9d651b', tmap_action)
standardCards.append(t)


# 84: Treasury
def treasury_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(1)(cM, gS, exc, tExc, pers)


t = Card('Treasury', 'Treasuries', 'a Treasury', 5, 0, 'c4c0b4', '884a00', treasury_action)
standardCards.append(t)


# 85: Warehouse
t = Card('Warehouse', 'Warehouses', 'a Warehouse', 3, 0, 'c4c0b4', '59635b', empty)
standardCards.append(t)

# 86: Wharf
t = Card('Wharf', 'Wharves', 'a Wharf', 5, 0, 'dda561', '7b778f', empty)
standardCards.append(t)

# 87: Alchemist
t = Card('Alchemist', 'Alchemists', 'an Alchemist', 5, 0, 'c4c0b4', '49A4E4', empty)
standardCards.append(t)

# 88: Apothecary
def apoth_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealTopdeck)


t = Card('Apothecary', 'Apothecaries', 'an Apothecary', 4, 0, 'c4c0b4', 'a36713', apoth_action)
standardCards.append(t)

# 89: Apprentice
t = Card('Apprentice', 'Apprentices', 'an Apprentice', 5, 0, 'c4c0b4', 'ce5800', empty)
standardCards.append(t)

# 90: Familiar
t = Card('Familiar', 'Familiars', 'a Familiar', 5, 0, 'c4c0b4', 'aa6656', empty)
standardCards.append(t)


# 91: Golem
def golem_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['PLAY'], 'DECKS', 'INPLAYS'))
        exc.append(Exception(standardCondition(['PLAY']), standardOnPlay))
        exc.append(exc_revealDiscard)


t = Card('Golem', 'Golems', 'a Golem', 6, 0, 'c4c0b4', '5e6c80', golem_action)
standardCards.append(t)


# 92: Herbalist
def herbalist_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['TOPDECK'], 'INPLAYS', 'DECKS'))


t = Card('Herbalist', 'Herbalists', 'a Herbalist', 2, 0, 'c4c0b4', 'b8884e', herbalist_action)
standardCards.append(t)

# 93: Philosopher\'s Stone
t = Card('Philosopher\'s Stone', 'Philosopher\'s Stones', 'a Philosopher\'s Stone', 5, 0, 'd8c280', '980642', empty)
standardCards.append(t)

# 94: Possession
t = Card('Possession', 'Possessions', 'a Possession', 8, 0, 'c4c0b4', '736157', empty)
standardCards.append(t)

# 95: Potion
t = Card('Potion', 'Potions', 'a Potion', 4, 2, 'f1d14d', '1768C4', empty)
standardCards.append(t)


# 96: Scrying Pool
def pool_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealTopdeck)
        exc.append(exc_revealDiscard)


t = Card('Scrying Pool', 'Scrying Pools', 'a Scrying Pool', 4, 0, 'c4c0b4', 'a45e08', pool_action)
standardCards.append(t)

# 97: Transmute
t = Card('Transmute', 'Transmutes', 'a Transmute', 2, 0, 'c4c0b4', '764a76', empty)
standardCards.append(t)

# 98: University
t = Card('University', 'Universities', 'a University', 4, 0, 'c4c0b4', '77714b', empty)
standardCards.append(t)


# 99: Vineyard
def vineyard_worth(gS, player):
    playerDeck = gS.crunch(['DECKS', 'DISCARDS', 'HANDS', 'OTHERS', 'INPLAYS'], [player])
    return sum([playerDeck[item] for item in playerDeck if
                standardCards[item].simple_name in actionList]) // 3


t = Card('Vineyard', 'Vineyards', 'a Vineyard', 2, 0, '9cbe8a', '8c9652', empty, vineyard_worth)
standardCards.append(t)

# 100: Bank
t = Card('Bank', 'Banks', 'a Bank', 7, 0, 'd8c280', '616745', empty)
standardCards.append(t)


# 101: Bishop
def bishop_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(1)(cM, gS, exc, tExc, pers)


t = Card('Bishop', 'Bishops', 'a Bishop', 4, 0, 'c4c0b4', '6a587c', bishop_action)
standardCards.append(t)

# 102: Colony
t = Card('Colony', 'Colonies', 'a Colony', 11, 2, '548C2B', '9494d8', empty, staticWorth(10))
standardCards.append(t)


# 103: Contraband
def contraband_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(3)(cM, gS, exc, tExc, pers)


t = Card('Contraband', 'Contrabands', 'a Contraband', 5, 0, 'd8c280', '68442c', contraband_action)
standardCards.append(t)


# 104: Counting House
def countinghouse_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['PUT INHAND'], 'DISCARDS', 'HANDS'))


t = Card('Counting House', 'Counting Houses', 'a Counting House', 5, 0, 'c4c0b4', '6f5143', countinghouse_action)
standardCards.append(t)

# 105: City
t = Card('City', 'Cities', 'a City', 5, 0, 'c4c0b4', 'a4a07c', empty)
standardCards.append(t)

# 106: Expand
t = Card('Expand', 'Expands', 'an Expand', 7, 0, 'c4c0b4', 'd77b07', empty)
standardCards.append(t)

# 107: Forge
t = Card('Forge', 'Forges', 'a Forge', 7, 0, 'c4c0b4', 'd05a2a', empty)
standardCards.append(t)


# 108: Grand Market
def gm_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(2)(cM, gS, exc, tExc, pers)


t = Card('Grand Market', 'Grand Markets', 'a Grand Market', 6, 0, 'c4c0b4', 'ab735b', gm_action)
standardCards.append(t)


# 109: Goons
def goons_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(2)(cM, gS, exc, tExc, pers)


t = Card('Goons', 'Goons', 'a Goons', 6, 0, 'c4c0b4', '6d6129', goons_action)
standardCards.append(t)


# 110: Hoard
def hoard_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(2)(cM, gS, exc, tExc, pers)


t = Card('Hoard', 'Hoards', 'a Hoard', 6, 0, 'd8c280', '917d25', hoard_action)
standardCards.append(t)

# 111: King\'s Court
t = Card('King\'s Court', 'King\'s Courts', 'a King\'s Court', 7, 0, 'c4c0b4', '926634', empty)
standardCards.append(t)


# 112: Loan
def loan_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(1)(cM, gS, exc, tExc, pers)
        exc.append(exc_revealTrash)
        exc.append(exc_standardTrash)
        exc.append(exc_revealDiscard)


t = Card('Loan', 'Loans', 'a Loan', 3, 0, 'd8c280', '9d936f', loan_action)
standardCards.append(t)


# 113: Mint
def mint_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['BUY AND GAIN', 'BUY']:
        exc.append(standardException(['TRASH'], 'INPLAYS', 'TRASH'))


t = Card('Mint', 'Mints', 'a Mint', 5, 0, 'c4c0b4', '7a5e40', mint_action)
standardCards.append(t)


# 114: Monument
def monument_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(2)(cM, gS, exc, tExc, pers)


t = Card('Monument', 'Monuments', 'a Monument', 4, 0, 'c4c0b4', '8191ab', monument_action)
standardCards.append(t)


# 115: Mountebank
def mountebank_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(2)(cM, gS, exc, tExc, pers)


t = Card('Mountebank', 'Mountebanks', 'a Mountebank', 5, 0, 'c4c0b4', '866a6a', mountebank_action)
standardCards.append(t)


# 116: Peddler
def peddler_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(1)(cM, gS, exc, tExc, pers)


t = Card('Peddler', 'Peddlers', 'a Peddler', 8, 0, 'c4c0b4', '9a5a2e', peddler_action)
standardCards.append(t)


# 117: Platinum
def platinum_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(5)(cM, gS, exc, tExc, pers)


t = Card('Platinum', 'Platina', 'a Platinum', 9, 2, 'f1d14d', '948266', platinum_action)
standardCards.append(t)


# 118: Quarry
def quarry_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(1)(cM, gS, exc, tExc, pers)


t = Card('Quarry', 'Quarries', 'a Quarry', 4, 0, 'd8c280', 'b9b59f', quarry_action)
standardCards.append(t)


# 119: Rabble
def rabble_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealTopdeck)
        exc.append(exc_revealDiscard)


t = Card('Rabble', 'Rabbles', 'a Rabble', 5, 0, 'c4c0b4', '88422c', rabble_action)
standardCards.append(t)


# 120: Royal Seal
def royalseal_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(2)(cM, gS, exc, tExc, pers)


t = Card('Royal Seal', 'Royal Seals', 'a Royal Seal', 5, 0, 'd8c280', 'd8b08e', royalseal_action)
standardCards.append(t)


# 121: Talisman
def talisman_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(1)(cM, gS, exc, tExc, pers)


t = Card('Talisman', 'Talismans', 'a Talisman', 4, 0, 'd8c280', 'b28038', talisman_action)
standardCards.append(t)

# 122: Trade Route
t = Card('Trade Route', 'Trade Routes', 'a Trade Route', 3, 0, 'c4c0b4', '65a167', empty)
standardCards.append(t)

# 123: Vault
t = Card('Vault', 'Vaults', 'a Vault', 5, 0, 'c4c0b4', '947e4e', empty)
standardCards.append(t)


# 124: Venture
def venture_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        gainCash(1)(cM, gS, exc, tExc, pers)
        exc.append(standardException(['PLAY'], 'DECKS', 'INPLAYS'))
        exc.append(Exception(standardCondition(['PLAY']), standardOnPlay))
        exc.append(standardException(['DISCARD'], 'DECKS', 'DISCARDS'))


t = Card('Venture', 'Ventures', 'a Venture', 5, 0, 'd8c280', '624e36', venture_action)
standardCards.append(t)

# 125: Watchtower
t = Card('Watchtower', 'Watchtowers', 'a Watchtower', 3, 0, '8ca2be', '7496c0', empty)
standardCards.append(t)

# 126: Worker\'s Village
t = Card('Worker\'s Village', 'Worker\'s Villages', 'a Worker\'s Village', 4, 0, 'c4c0b4', 'cd7119', empty)
standardCards.append(t)

# 127: Prize Pile
t = Card('Prize Pile', 'Prize Piles', 'a Prize Pile', 0, 0, '666666', '666666', empty)
standardCards.append(t)


# 128: Bag of Gold
def bagofgold_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['GAIN'], 'SUPPLY', 'DECKS', ['Gold']))
        exc.append(Exception(standardCondition(['GAIN'], ['Gold']),
                             standardOnGains('DECKS')))


t = Card('Bag of Gold', 'Bags of Gold', 'a Bag of Gold', 0, 1, 'c4c0b4', 'b47214', bagofgold_action)
standardCards.append(t)

# 129: Diadem
t = Card('Diadem', 'Diadems', 'a Diadem', 0, 1, 'd8c280', 'ffba14', empty)
standardCards.append(t)


# 130: Fairgrounds
def fairgrounds_worth(gS, player):
    playerDeck = gS.crunch(['DECKS', 'DISCARDS', 'HANDS', 'OTHERS', 'INPLAYS'], [player])
    return len(playerDeck.cardList()) // 5


t = Card('Fairgrounds', 'Fairgrounds', 'a Fairgrounds', 6, 0, '9cbe8a', '9a8462', empty, fairgrounds_worth)
standardCards.append(t)


# 131: Farming Village
def farmvillage_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealDiscard)


t = Card('Farming Village', 'Farming Villages', 'a Farming Village', 4, 0, 'c4c0b4', '8d7f67', farmvillage_action)
standardCards.append(t)

# 132: Followers
t = Card('Followers', 'Followers', 'a Followers', 0, 1, 'c4c0b4', 'ab670b', empty)
standardCards.append(t)


# 133: Fortune Teller
def fortuneteller_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealTopdeck)
        exc.append(exc_revealDiscard)

t = Card('Fortune Teller', 'Fortune Tellers', 'a Fortune Teller', 3, 0, 'c4c0b4', '884214', fortuneteller_action)
standardCards.append(t)

# 134: Hamlet
t = Card('Hamlet', 'Hamlets', 'a Hamlet', 2, 0, 'c4c0b4', '8e9886', empty)
standardCards.append(t)

# 135: Harvest
def harvest_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealDiscard)

t = Card('Harvest', 'Harvests', 'a Harvest', 5, 0, 'c4c0b4', 'cd9f49', harvest_action)
standardCards.append(t)


# 136: Horse Traders
def horseTraders_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() == 'REACT':
        tExc.append(standardException(['SET ASIDE'], 'HANDS', 'OTHERS',
                                      ['Horse Traders']))


t = Card('Horse Traders', 'Horse Traders', 'a Horse Traders', 4, 0, '8ca2be', '595561', horseTraders_action)
standardCards.append(t)

# 137: Horn of Plenty
def hop_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['TRASH'], 'INPLAYS', 'TRASH',
                                     ['Horn of Plenty']))

t = Card('Horn of Plenty', 'Horns of Plenty', 'a Horn of Plenty', 5, 0, 'd8c280', '7b4d27', hop_action)
standardCards.append(t)

# 138: Hunting Party
def huntingparty_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealDiscard)

t = Card('Hunting Party', 'Hunting Parties', 'a Hunting Party', 5, 0, 'c4c0b4', '4e4e48', huntingparty_action)
standardCards.append(t)

# 139: Jester
def jester_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealDiscard)

t = Card('Jester', 'Jesters', 'a Jester', 5, 0, 'c4c0b4', '9f7967', jester_action)
standardCards.append(t)

# 140: Menagerie
t = Card('Menagerie', 'Menageries', 'a Menagerie', 3, 0, 'c4c0b4', '8a7234', empty)
standardCards.append(t)

# 141: Princess
t = Card('Princess', 'Princesses', 'a Princess', 0, 1, 'c4c0b4', '804e10', empty)
standardCards.append(t)

# 142: Remake
t = Card('Remake', 'Remakes', 'a Remake', 4, 0, 'c4c0b4', 'b46614', empty)
standardCards.append(t)


# 143: Tournament
def tournament_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['GAIN'], 'SUPPLY', 'DECKS'))
        exc.append(Exception(standardCondition(['GAIN']),
                             standardOnGains('DECKS')))


t = Card('Tournament', 'Tournaments', 'a Tournament', 4, 0, 'c4c0b4', '937755', tournament_action)
standardCards.append(t)


# 144: Trusty Steed
def steed_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['GAIN'], 'SUPPLY', 'DECKS', ['Silver']))
        exc.append(Exception(standardCondition(['GAIN']),
                             standardOnGains('DECKS')))


t = Card('Trusty Steed', 'Trusty Steeds', 'a Trusty Steed', 0, 1, 'c4c0b4', '6e726a', steed_action)
standardCards.append(t)

# 145: Young Witch
t = Card('Young Witch', 'Young Witches', 'a Young Witch', 4, 0, 'c4c0b4', '7b653b', empty)
standardCards.append(t)

# 146: Border Village
t = Card('Border Village', 'Border Villages', 'a Border Village', 6, 0, 'c4c0b4', '758791', empty)
standardCards.append(t)

# 147: Cache
t = Card('Cache', 'Caches', 'a Cache', 5, 0, 'd8c280', '6e7846', empty)
standardCards.append(t)


# 148: Cartographer
def cartographer_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealDiscard)
        exc.append(exc_revealTopdeck)


t = Card('Cartographer', 'Cartographers', 'a Cartographer', 5, 0, 'c4c0b4', 'a45a14', cartographer_action)
standardCards.append(t)

# 149: Crossroads
t = Card('Crossroads', 'Crossroads', 'a Crossroads', 2, 0, 'c4c0b4', 'a7a187', empty)
standardCards.append(t)


# 150: Develop
def develop_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['GAIN'], 'SUPPLY', 'DECKS'))
        exc.append(Exception(standardCondition(['GAIN']),
                             standardOnGains('DECKS')))


t = Card('Develop', 'Develops', 'a Develop', 3, 0, 'c4c0b4', 'c09864', develop_action)
standardCards.append(t)


# 151: Duchess
def duchess_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealDiscard)
        exc.append(exc_revealTopdeck)


t = Card('Duchess', 'Duchesses', 'a Duchess', 2, 0, 'c4c0b4', '999b77', duchess_action)
standardCards.append(t)

# 152: Embassy
t = Card('Embassy', 'Embassies', 'an Embassy', 5, 0, 'c4c0b4', '8e725c', empty)
standardCards.append(t)

# 153: Farmland
t = Card('Farmland', 'Farmlands', 'a Farmland', 6, 0, '9cbe8a', '4fbb9d', empty, staticWorth(2))
standardCards.append(t)


# 154: Fool\'s Gold
def fg_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['TRASH']:
        tExc.append(standardException(['GAIN'], 'SUPPLY', 'DECKS', ['Gold']))


t = Card('Fool\'s Gold', 'Fool\'s Golds', 'a Fool\'s Gold', 2, 0, '939E9D', 'b8a62e', fg_action)
standardCards.append(t)

# 155: Haggler
t = Card('Haggler', 'Hagglers', 'a Haggler', 5, 0, 'c4c0b4', 'a07a56', empty)
standardCards.append(t)

# 156: Highway
t = Card('Highway', 'Highways', 'a Highway', 5, 0, 'c4c0b4', 'a0be8c', empty)
standardCards.append(t)


# 157: Ill-Gotten Gains
def igg_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        tExc.append(standardException(['GAIN'], 'SUPPLY', 'HANDS', ['Copper']))


t = Card('Ill-Gotten Gains', 'Ill-Gotten Gains', 'an Ill-Gotten Gains', 5, 0, 'd8c280', '9d6d41', igg_action)
standardCards.append(t)

# 158: Inn
t = Card('Inn', 'Inns', 'an Inn', 5, 0, 'c4c0b4', '71957d', empty)
standardCards.append(t)


# 159: Jack of All Trades
def jack_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealDiscard)
        exc.append(exc_revealTopdeck)


t = Card('Jack of All Trades', 'Jacks of All Trades', 'a Jack of All Trades', 4, 0, 'c4c0b4', '7aa2a4', jack_action)
standardCards.append(t)


# 160: Mandarin
def mandarin_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['BUY AND GAIN', 'GAIN TOPDECK',
                            'GAIN TRASH', 'GAIN']:
        exc.append(standardException(['TOPDECK'], 'INPLAYS', 'DECKS'))


t = Card('Mandarin', 'Mandarins', 'a Mandarin', 5, 0, 'c4c0b4', 'b38f2d', mandarin_action)
standardCards.append(t)


# 161: Noble Brigand
def brigand_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD', 'BUY']:
        exc.append(exc_revealTrash)
        exc.append(exc_standardTrash)
        exc.append(exc_revealDiscard)


t = Card('Noble Brigand', 'Noble Brigands', 'a Noble Brigand', 4, 0, 'c4c0b4', '645c46', brigand_action)
standardCards.append(t)

# 162: Nomad Camp
t = Card('Nomad Camp', 'Nomad Camps', 'a Nomad Camp', 4, 0, 'c4c0b4', '87a1b1', empty)
standardCards.append(t)

# 163: Oasis
t = Card('Oasis', 'Oases', 'an Oasis', 3, 0, 'c4c0b4', '8e9864', empty)
standardCards.append(t)


# 164: Oracle
def oracle_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealDiscard)
        exc.append(exc_revealTopdeck)


t = Card('Oracle', 'Oracles', 'an Oracle', 3, 0, 'c4c0b4', '69491b', oracle_action)
standardCards.append(t)

# 165: Margrave
t = Card('Margrave', 'Margraves', 'a Margrave', 5, 0, 'c4c0b4', '7c6c48', empty)
standardCards.append(t)

# 166: Scheme
t = Card('Scheme', 'Schemes', 'a Scheme', 3, 0, 'c4c0b4', '7f7d7d', empty)
standardCards.append(t)


# 167: Silk Road
def silkroad_worth(gameState, player):
    playerDeck = gameState.crunch(['DECKS', 'DISCARDS', 'HANDS',
                                   'OTHERS', 'INPLAYS'], [player])
    return sum([playerDeck[item] for item in playerDeck if
                standardCards[item].simple_name in victoryCards])//4


t = Card('Silk Road', 'Silk Roads', 'a Silk Road', 4, 0, '9cbe8a', '948452', empty, silkroad_worth)
standardCards.append(t)

# 168: Spice Merchant
t = Card('Spice Merchant', 'Spice Merchants', 'a Spice Merchant', 4, 0, 'c4c0b4', 'af7b4d', empty)
standardCards.append(t)

# 169: Stables
t = Card('Stables', 'Stables', 'a Stables', 5, 0, 'c4c0b4', '875d33', empty)
standardCards.append(t)

# 170: Trader
t = Card('Trader', 'Traders', 'a Trader', 4, 0, '8ca2be', '988a34', empty)
standardCards.append(t)

# 171: Tunnel
t = Card('Tunnel', 'Tunnels', 'a Tunnel', 3, 0, '879E96', '545258', empty, staticWorth(2))
standardCards.append(t)

# 172: Ruins
t = Card('Ruins', 'Ruins', 'a Ruins', 0, 2, 'b29462', '666666', empty)
standardCards.append(t)

# 173: Knights
t = Card('Knights', 'Knights', 'a Knights', 5, 0, 'c4c0b4', '819381', empty)
standardCards.append(t)

# 174: Abandoned Mine
t = Card('Abandoned Mine', 'Abandoned Mines', 'an Abandoned Mine', 0, -1, 'b29462', '633b29', empty)
standardCards.append(t)

# 175: Altar
t = Card('Altar', 'Altars', 'an Altar', 6, 0, 'c4c0b4', '7e3800', empty)
standardCards.append(t)


# 176: Armory
def armory_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['GAIN'], 'SUPPLY', 'DECKS'))
        exc.append(Exception(standardCondition(['GAIN']),
                             standardOnGains('DECKS')))


t = Card('Armory', 'Armories', 'an Armory', 4, 0, 'c4c0b4', '54564e', armory_action)
standardCards.append(t)

# 177: Band of Misfits
def BoM_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['PLAY'], 'SUPPLY', 'SUPPLY'))
        exc.append(Exception(standardCondition(['PLAY']), standardOnPlay))


t = Card('Band of Misfits', 'Bands of Misfits', 'a Band of Misfits', 5, 0, 'c4c0b4', '56505c', BoM_action)
standardCards.append(t)

# 178: Bandit Camp
t = Card('Bandit Camp', 'Bandit Camps', 'a Bandit Camp', 5, 0, 'c4c0b4', '42889e', empty)
standardCards.append(t)


# 179: Beggar
def beggar_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['GAIN'], 'SUPPLY', 'HANDS', ['Copper']))
        exc.append(Exception(standardCondition(['GAIN'], ['Copper']),
                             standardOnGains('HANDS')))


t = Card('Beggar', 'Beggars', 'a Beggar', 2, 0, '8ca2be', '503626', beggar_action)
standardCards.append(t)


# 180: Catacombs
def catacombs_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealDiscard)


t = Card('Catacombs', 'Catacombs', 'a Catacombs', 5, 0, 'c4c0b4', '472f1f', catacombs_action)
standardCards.append(t)

# 181: Count
t = Card('Count', 'Counts', 'a Count', 5, 0, 'c4c0b4', '58605c', empty)
standardCards.append(t)


# 182: Counterfeit
def counterfeit_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_inplayTrash)
        exc.append(exc_standardTrash)


t = Card('Counterfeit', 'Counterfeits', 'a Counterfeit', 5, 0, 'd8c280', 'a66e28', counterfeit_action)
standardCards.append(t)

# 183: Cultist
t = Card('Cultist', 'Cultists', 'a Cultist', 5, 0, 'c4c0b4', '4b4957', empty)
standardCards.append(t)


def knightsSuicideCondition(knightPlayer):
    def out_function(cM):
        isKnight = cM[0].items.primary() in knights
        return cM[0].predName() == 'TRASH' and cM[0].player == knightPlayer and isKnight
    return out_function


def standardKnightsAction(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealDiscard)
        exc.append(Exception(knightsTrashCondition(cM[0].player),
                             moveException('DECKS', 'TRASH')))
        exc.append(Exception(knightsTrashCondition(cM[0].player),
                             standardOnTrash))
        exc.append(Exception(knightsSuicideCondition(cM[0].player),
                             moveException('INPLAYS', 'TRASH')))


# 184: Dame Anna
def anna_trash_condition(knightPlayer):
    def out_function(cM):
        trashPart = cM[0].predName() == 'TRASH' and cM[0].items.primary() != 'Dame Anna'
        return trashPart and cM[0].player == knightPlayer
    return out_function


def anna_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealDiscard)
        exc.append(Exception(knightsTrashCondition(cM[0].player),
                             moveException('DECKS', 'TRASH')))
        exc.append(Exception(knightsTrashCondition(cM[0].player),
                             standardOnTrash))
        exc.append(Exception(knightsSuicideCondition(cM[0].player),
                             moveException('INPLAYS', 'TRASH')))
        exc.append(Exception(anna_trash_condition(cM[0].player),
                             moveException('HANDS', 'TRASH')))
        exc.append(Exception(anna_trash_condition(cM[0].player),
                             standardOnTrash))


t = Card('Dame Anna', 'Dame Annas', 'a Dame Anna', 5, -1, 'c4c0b4', '775f35', anna_action)
standardCards.append(t)


# 185: Dame Josephine
t = Card('Dame Josephine', 'Dame Josephines', 'a Dame Josephine', 5, -1,
         'aac298', '635147', standardKnightsAction, staticWorth(2))
standardCards.append(t)

# 186: Dame Molly
t = Card('Dame Molly', 'Dame Mollies', 'a Dame Molly', 5, -1, 'c4c0b4', '946e50', standardKnightsAction)
standardCards.append(t)

# 187: Dame Natalie
t = Card('Dame Natalie', 'Dame Natalies', 'a Dame Natalie', 5, -1, 'c4c0b4', '56665a', standardKnightsAction)
standardCards.append(t)

# 188: Dame Sylvia
t = Card('Dame Sylvia', 'Dame Sylvias', 'a Dame Sylvia', 5, -1, 'c4c0b4', '744c36', standardKnightsAction)
standardCards.append(t)

# 189: Death Cart
def deathcart_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['TRASH'], 'INPLAYS', 'TRASH', ['Death Cart']))
        exc.append(Exception(standardCondition(['TRASH'], ['Death Cart']), standardOnTrash))


t = Card('Death Cart', 'Death Carts', 'a Death Cart', 4, 0, 'c4c0b4', '826636', deathcart_action)
standardCards.append(t)


# 190: Feodum
def feodum_worth(gameState, player):
    playerDeck = gameState.crunch(['DECKS', 'DISCARDS', 'HANDS',
                                   'OTHERS', 'INPLAYS'], [player])

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
def fortress_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['TRASH']:
        exc.append(standardException(['PUT INHAND'], 'TRASH', 'HANDS'))


t = Card('Fortress', 'Fortresses', 'a Fortress', 4, 0, 'c4c0b4', '62524c', fortress_action)
standardCards.append(t)


# 193: Graverobber
def graverobber_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        isRemodelling = False
        for chunk in cM[1:]:
            if chunk[0].predName() == 'TRASH':
                isRemodelling = True

        if not isRemodelling:
            exc.append(standardException(['GAIN'], 'TRASH', 'DECKS'))


t = Card('Graverobber', 'Graverobbers', 'a Graverobber', 5, 0, 'c4c0b4', '4e4052', graverobber_action)
standardCards.append(t)


# 194: Hermit
def hermit_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        playerDiscard = gS[-1].DISCARDS[cM[0].player]

        def hermitTrashCondition(playerDiscard):
            def out_function(cM):
                return (cM[0].items - playerDiscard).count() == 0 and cM[0].predName() == 'TRASH'
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
def ironmonger_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
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
def pillage_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['TRASH'], 'INPLAYS', 'TRASH',
                                     ['Pillage']))


t = Card('Pillage', 'Pillages', 'a Pillage', 5, 0, 'c4c0b4', '8d7f63', pillage_action)
standardCards.append(t)

# 207: Poor House
t = Card('Poor House', 'Poor Houses', 'a Poor House', 1, 0, 'c4c0b4', '65573d', empty)
standardCards.append(t)


# 208: Procession
def procession_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_inplayTrash)
        exc.append(exc_standardTrash)


t = Card('Procession', 'Processions', 'a Procession', 4, 0, 'c4c0b4', '775f3d', procession_action)
standardCards.append(t)

# 209: Rats
t = Card('Rats', 'Rats', 'a Rats', 4, 0, 'c4c0b4', '795743', empty)
standardCards.append(t)


# 210: Rebuild
def rebuild_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealTrash)
        exc.append(exc_revealDiscard)


t = Card('Rebuild', 'Rebuilds', 'a Rebuild', 5, 0, 'c4c0b4', '64748c', rebuild_action)
standardCards.append(t)


# 211: Rogue
def rogue_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['GAIN'], 'TRASH', 'DISCARDS'))
        exc.append(Exception(standardCondition(['GAIN']),
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
def sage_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealDiscard)


t = Card('Sage', 'Sages', 'a Sage', 3, 0, 'c4c0b4', '89612f', sage_action)
standardCards.append(t)


# 216: Scavenger
def scavenger_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
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
def michael_action(cM, gS, exc, tExc, pers):
    def michaelRevealException(outerExceptions):
        def out_function(cM, gS, exc, tExc, pers):
            outerExceptions.append(exc_revealDiscard)
        return out_function

    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(Exception(knightsTrashCondition(cM[0].player),
                             moveException('DECKS', 'TRASH')))
        exc.append(exc_standardTrash)
        exc.append(Exception(standardCondition(['REVEAL']),
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
def survivors_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealTopdeck)
        exc.append(exc_revealDiscard)


t = Card('Survivors', 'Survivors', 'a Survivors', 0, -1, 'b29462', '706a46', survivors_action)
standardCards.append(t)

# 226: Urchin
t = Card('Urchin', 'Urchins', 'an Urchin', 3, 0, 'c4c0b4', '634b33', empty)
standardCards.append(t)


# 227: Vagrant
def vagrant_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealTopdeck)


t = Card('Vagrant', 'Vagrants', 'a Vagrant', 2, 0, 'c4c0b4', '593f2b', vagrant_action)
standardCards.append(t)


# 228: Wandering Minstrel
def minstrel_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealTopdeck)
        exc.append(exc_revealDiscard)


t = Card('Wandering Minstrel', 'Wandering Minstrels', 'a Wandering Minstrel', 4, 0, 'c4c0b4', '905414', minstrel_action)
standardCards.append(t)


# 229: Advisor
def advisor_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
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
def doctor_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD', 'BUY']:
        exc.append(exc_revealTopdeck)
        exc.append(exc_revealDiscard)
        exc.append(exc_revealTrash)
        exc.append(exc_standardTrash)


t = Card('Doctor', 'Doctors', 'a Doctor', 3, 0, 'c4c0b4', '895923', doctor_action)
standardCards.append(t)


# 234: Herald
def herald_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['PLAY'], 'DECKS', 'INPLAYS'))
        exc.append(Exception(standardCondition(['PLAY']), standardOnPlay))

    if cM[0].predName() in ['BUY']:
        exc.append(exc_harbinger)


t = Card('Herald', 'Heralds', 'a Herald', 4, 0, 'c4c0b4', '996941', herald_action)
standardCards.append(t)


# 235: Journeyman
def journeyman_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
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
def taxman_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['GAIN'], 'SUPPLY', 'DECKS'))
        exc.append(Exception(standardCondition(['GAIN']),
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
def artificer_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['GAIN'], 'SUPPLY', 'DECKS'))
        exc.append(Exception(standardCondition(['GAIN']),
                             standardOnGains('DECKS')))


t = Card('Artificer', 'Artificers', 'an Artificer', 5, 0, 'c4c0b4', '754f2b', artificer_action)
standardCards.append(t)

# 245: Ball
t = Card('Ball', 'Balls', 'a Ball', 5, 2, 'a9a39d', '8b6323', empty)
standardCards.append(t)


# 246: Bonfire
def bonfire_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['BUY']:
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
def standard_reserve(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['PUT ONTO'], 'INPLAYS', 'OTHERS'))


t = Card('Coin of the Realm', 'Coins of the Realm', 'a Coin of the Realm', 2, 0, 'c2a85c', 'ae6c00', standard_reserve)
standardCards.append(t)

# 252: Disciple
t = Card('Disciple', 'Disciples', 'a Disciple', 5, 1, 'c2bfba', '966a2c', empty)
standardCards.append(t)


# 253: Distant Lands
def distantlands_worth(gS, player):
    playerDeck = gS.crunch(['DECKS', 'OTHERS'], [player])
    DLCard = standardNames.index('Distant Lands')
    for card in playerDeck:
        if standardCards[card].simple_name == 'Distant Lands':
            total = playerDeck[card]
            break

    if DLCard in gS.OTHERS[player]:
        return gS.OTHERS[player][DLCard] / total
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
def giant_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
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
def magpie_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
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
def raze_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['TRASH'], 'INPLAYS', 'TRASH', ['Raze']))
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
def save_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['BUY']:
        tExc.append(standardException(['PUT INHAND'], 'OTHERS', 'HANDS'))

t = Card('Save', 'Saves', 'a Save', 1, 2, 'a9a39d', '814d3b', save_action)
standardCards.append(t)

# 286: Scouting Party
def scoutingparty_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['BUY']:
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
def transmogrify_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['PUT ONTO'], 'INPLAYS', 'OTHERS'))

    if cM[0].predName() in ['CALL']:
        tExc.append(standardException(['GAIN'], 'SUPPLY', 'HANDS'))
        tExc.append(Exception(standardCondition(['GAIN']),
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
def warrior_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealDiscard)
        exc.append(standardException(['TRASH'], 'DISCARDS', 'TRASH'))
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
def patrician_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealTopdeck)


t = Card('Patrician', 'Patricians', 'a Patrician', 2, 0, 'c4c0b4', '6a80a0', patrician_action)
standardCards.append(t)

# 303: Emporium
t = Card('Emporium', 'Emporia', 'an Emporium', 5, 0, 'c4c0b4', '50ABDF', empty)
standardCards.append(t)


# 304: Settlers
def settlers_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['PUT INHAND'], 'DISCARDS', 'HANDS'))


t = Card('Settlers', 'Settlers', 'a Settlers', 2, 0, 'c4c0b4', '784624', settlers_action)
standardCards.append(t)


# 305: Bustling Village
def bustvillage_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['PUT INHAND'], 'DISCARDS', 'HANDS'))


t = Card('Bustling Village', 'Bustling Villages', 'a Bustling Village', 5, 0, 'c4c0b4', '745E4D', bustvillage_action)
standardCards.append(t)

# 306: Catapult
t = Card('Catapult', 'Catapults', 'a Catapult', 3, 0, 'c4c0b4', '839f55', empty)
standardCards.append(t)


# 307: Rocks
def rocks_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['BUY AND GAIN', 'GAIN TOPDECK',
                            'GAIN TRASH', 'GAIN']:
        if gS[-1].phase == 1:
            exc.append(standardException(['GAIN'], 'SUPPLY', 'DECKS'))
            exc.append(Exception(standardCondition(['GAIN']),
                                 standardOnGains('DECKS')))
        else:
            exc.append(standardException(['GAIN'], 'SUPPLY', 'HANDS'))
            exc.append(Exception(standardCondition(['GAIN']),
                                 standardOnGains('HANDS'))) 


t = Card('Rocks', 'Rocks', 'a Rocks', 4, 0, 'd8c280', '80963a', rocks_action)
standardCards.append(t)


# 308: Gladiator
def gladiator_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['TRASH'], 'SUPPLY', 'TRASH',
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
                            'OTHERS', 'INPLAYS'], [player])
    return sum([playerDeck[item] for item in playerDeck if
                standardCards[item].simple_name in castles])


t = Card('Humble Castle', 'Humble Castles', 'a Humble Castle', 3, -1, 'a9c35d', '63af7f', empty, humbleCastle_worth)
standardCards.append(t)

# 312: Crumbling Castle
t = Card('Crumbling Castle', 'Crumbling Castles', 'a Crumbling Castle', 4, -1, '9cbe8a', 'ceb22c', empty, staticWorth(1))
standardCards.append(t)


# 313: Small Castle
def smallcastle_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['TRASH'], 'INPLAYS', 'TRASH',
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
                            'OTHERS', 'INPLAYS'], [player])
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
def archive_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['SET ASIDE'], 'DECKS', 'OTHERS'))


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
    playerDeck = gameState.crunch(['DECKS', 'DISCARDS', 'HANDS', 'OTHERS', 'INPLAYS'], [player])
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
def chariotrace_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
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
def engineer_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        def engineerTrashCondition(cM):
            return cM[0].indent == 0 and \
                   cM[0].predName() == 'TRASH' and \
                   cM[0].items.primary() == 'Engineer'

        if cM[0].indent == 0:
            tExc.append(Exception(engineerTrashCondition, moveException('INPLAYS', 'TRASH'), chunkLength(cM) + 2))
            exc.append(standardException(['TRASH'], 'INPLAYS', 'TRASH', ['Engineer']))
        else:
            exc.append(standardException(['TRASH'], 'INPLAYS', 'TRASH', ['Engineer']))


t = Card('Engineer', 'Engineers', 'an Engineer', 4, 0, 'c4c0b4', '733719', engineer_action)
standardCards.append(t)


# 342: Farmers' Market
def farmmarket_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['TRASH'], 'INPLAYS', 'TRASH',
                                     ['Farmers\' Market']))


t = Card('Farmers\' Market', 'Farmers\' Markets', 'a Farmers\' Market', 3, 0, 'c4c0b4', '867642', farmmarket_action)
standardCards.append(t)

# 343: Forum
t = Card('Forum', 'Forums', 'a Forum', 5, 0, 'c4c0b4', 'bc9256', empty)
standardCards.append(t)


# 344: Fountain
def fountain_worth(gameState, player):
    playerDeck = gameState.crunch(['DECKS', 'DISCARDS', 'HANDS', 'OTHERS', 'INPLAYS'], [player])
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
    playerDeck = gameState.crunch(['DECKS', 'DISCARDS', 'HANDS', 'OTHERS', 'INPLAYS'], [player])
    otherDeck = gameState.crunch(['DECKS', 'DISCARDS', 'HANDS', 'OTHERS', 'INPLAYS'], [1 - player])
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
    playerDeck = gameState.crunch(['DECKS', 'DISCARDS', 'HANDS', 'OTHERS', 'INPLAYS'], [player])
    return 2 * len(playerDeck.cardList())

t = Card('Museum', 'Museums', 'a Museum', 0, 2, '65ab6f', 'c47a00', empty, museum_worth)
standardCards.append(t)


# 351: Obelisk
def obelisk_worth(gameState, player):
    playerDeck = gameState.crunch(['DECKS', 'DISCARDS', 'HANDS', 'OTHERS', 'INPLAYS'], [player])

    if gameState.obelisk in playerDeck:
        return playerDeck[obelisk]
    else:
        return 0


t = Card('Obelisk', 'Obelisks', 'an Obelisk', 0, 2, '65ab6f', '774d29', empty, obelisk_worth)
standardCards.append(t)


# 352: Orchard
def orchard_worth(gameState, player):
    playerDeck = gameState.crunch(['DECKS', 'DISCARDS', 'HANDS', 'OTHERS', 'INPLAYS'], [player])
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
    playerDeck = gameState.crunch(['DECKS', 'DISCARDS', 'HANDS', 'OTHERS', 'INPLAYS'], [player])
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
def salt_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['BUY']:
        exc.append(Exception(standardCondition(['TRASH']), moveException('SUPPLY', 'TRASH')))

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
    playerDeck = gameState.crunch(['DECKS', 'DISCARDS', 'HANDS', 'OTHERS', 'INPLAYS'], [player])
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
    playerDeck = gameState.crunch(['DECKS', 'DISCARDS', 'HANDS', 'OTHERS', 'INPLAYS'], [player])
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
    playerDeck = gameState.crunch(['DECKS', 'DISCARDS', 'HANDS', 'OTHERS', 'INPLAYS'], [player])
    size = gameState.crunch(['DECKS', 'HANDS', 'DISCARDS', 'OTHERS', 'INPLAYS'], [player]).count()
    return 15 - max(15, size)

t = Card('Wall', 'Walls', 'a Wall', 0, 2, '65ab6f', '5e4a54', empty, wall_worth)
standardCards.append(t)

# 367: Wolf Den
def den_worth(gameState, player):
    playerDeck = gameState.crunch(['DECKS', 'DISCARDS', 'HANDS', 'OTHERS', 'INPLAYS'], [player])
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
def miserable_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() == ['TAKES']:
        gS[-1].vps[cM[0].player] -= 2

t = Card('Miserable', 'Miserables', 'Miserable', 0, -1, 'ceb0a4', '1c161a', miserable_action)
standardCards.append(t)

# 400: Twice Miserable
def twicemiserable_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() == ['TAKES']:
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
def changeling_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
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
def druid_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        whichBoon = standardCards[CARD_CARD]
        exc.append(Exception(standardCondition('RECEIVE BOONHEX'), empty))
        for subchunk in cM[1:]:
            if subchunk[0].predName() in ['RECEIVE BOONHEX', 'TAKES BOONHEX']:
                whichBoon = subchunk[0].items.primary()
                break
            exc.append(standardException(['TRASH'], 'INPLAYS', 'TRASH'))

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
def hound_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['REACT']:
        tExc.append(standardException(['SET ASIDE'], 'DISCARDS', 'OTHERS', ['Faithful Hound']))


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
def monastery_action(cM, gS, exc, tExc, pers):
    #Possible conflicts: Exorcist - hence, trash inplay first.
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        def monastery_trash(cM, gS, exc, tExc, pers):
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

        exc.append(Exception(standardCondition(['TRASH'], ['Copper']),
                             monastery_trash))
        exc.append(exc_standardTrash)


t = Card('Monastery', 'Monasteries', 'a Monastery', 2, 0, '30484e', '02268a', monastery_action)
standardCards.append(t)


# 423: Necromancer
def necromancer_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['PLAY'], 'TRASH', 'TRASH'))
        exc.append(Exception(standardCondition(['PLAY']),  standardOnPlay))


t = Card('Necromancer', 'Necromancers', 'a Necromancer', 4, 0, 'c4c0b4', '525a36', necromancer_action)
standardCards.append(t)


# 424: Night Watchman
def watchman_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealDiscard)
        exc.append(exc_revealTopdeck)


t = Card('Night Watchman', 'Night Watchmen', 'a Night Watchman', 3, 0, '30484e', '464266', watchman_action)
standardCards.append(t)


# 425: Pixie
def pixie_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        whichBoon = standardCards[CARD_CARD]
        exc.append(Exception(standardCondition('RECEIVE BOONHEX'), empty))
        for subchunk in cM[1:]:
            if subchunk[0].predName() in ['RECEIVE BOONHEX', 'TAKES BOONHEX']:
                whichBoon = subchunk[0].items.primary()
                break

        if whichBoon == 'The Flame\'s Gift':
            pixieStack = Cardstack({standardNames.index('Pixie'): 1})
            otherThings = cM[0].items - pixieStack

            def pixieTrash(pixieStack, otherThings):
                def out_function(cM, gS, exc, tExc, pers):
                    gS[-1].move(cM[0].player, 'INPLAYS', 'TRASH',
                                        pixieStack)
                    gS[-1].move(cM[0].player, 'HANDS', 'TRASH',
                                        otherThings)
                return out_function

            exc.append(Exception(standardCondition(['TRASH'], ['Pixie']),
                                 pixieTrash(pixieStack, otherThings)))
            exc.append(Exception(standardCondition(['TRASH'], ['Pixie']), standardOnTrash))
        else:
            exc.append(standardException(['TRASH'], 'INPLAYS', 'TRASH'))

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
def tragichero_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['TRASH'], 'INPLAYS', 'TRASH',
                                     ['Tragic Hero', 'Overlord']))


t = Card('Tragic Hero', 'Tragic Heroes', 'a Tragic Hero', 5, 0, 'c4c0b4', '5c88a4', tragichero_action)
standardCards.append(t)

# 434: Tracker
t = Card('Tracker', 'Trackers', 'a Tracker', 2, 0, 'c4c0b4', '87c7d9', empty)
standardCards.append(t)


# 435: Vampire
def vampire_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['RETURN'], 'INPLAYS', 'SUPPLY',
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
def lamp_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['TRASH'], 'INPLAYS', 'TRASH',
                                     ['Magic Lamp']))


t = Card('Magic Lamp', 'Magic Lamps', 'a Magic Lamp', 0, 2, 'd8c280', '8c3400', lamp_action)
standardCards.append(t)


# 442: Pasture
def pasture_worth(gameState, player):
    playerDeck = gameState.crunch(['DECKS', 'DISCARDS', 'HANDS',
                                   'OTHERS', 'INPLAYS'], [player])
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
def bat_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['RETURN'], 'INPLAYS', 'SUPPLY', ['Bat']))


t = Card('Bat', 'Bats', 'a Bat', 2, 1, '30484e', '475B5D', bat_action)
standardCards.append(t)


# 445: Ghost
def ghost_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealDiscard)
        exc.append(standardException(['SET ASIDE'], 'DECKS', 'OTHERS'))


t = Card('Ghost', 'Ghosts', 'a Ghost', 4, 1, '7a5622', '13b12f', ghost_action)
standardCards.append(t)


# 446: Imp
t = Card('Imp', 'Imps', 'an Imp', 2, 1, 'c4c0b4', '936d69', empty)
standardCards.append(t)


# 447: Will-o'-wisp
def wisp_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealTopdeck)


t = Card('Will-o\'-wisp', 'Will-o\'-wisps', 'a Will-o\'-wisp', 0, 1, 'c4c0b4', '1d593f', wisp_action)
standardCards.append(t)


# 448: Wish
def wish_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['GAIN'], 'SUPPLY', 'HANDS',))
        exc.append(Exception(standardCondition(['GAIN']),
                             standardOnGains('HANDS')))


t = Card('Wish', 'Wishes', 'a Wish', 0, 1, 'c4c0b4', '0f6551', wish_action)
standardCards.append(t)

# 449: Zombie Apprentice
t = Card('Zombie Apprentice', 'Zombie Apprentices', 'a Zombie Apprentice', 3, 1, 'c4c0b4', '292d23', empty)
standardCards.append(t)

# 450: Zombie Mason
def zombiemason_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['TRASH'], 'DECKS', 'TRASH'))
        exc.append(exc_standardTrash)

t = Card('Zombie Mason', 'Zombie Masons', 'a Zombie Mason', 3, 1, 'c4c0b4', '5f513d', zombiemason_action)
standardCards.append(t)

# 451: Zombie Spy
def zombiespy_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
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
def envoy_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(exc_revealDiscard)

t = Card('Envoy', 'Envoys', 'an Envoy', 4, 0, 'c4c0b4', '425064', envoy_action)
standardCards.append(t)

# 455: Governor
t = Card('Governor', 'Governors', 'a Governor', 5, 0, 'c4c0b4', '8f9989', empty)
standardCards.append(t)

# 456: Prince
def prince_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['PLAY', 'PLAY AGAIN', 'PLAY THIRD']:
        exc.append(standardException(['SET ASIDE'], 'HANDS', 'OTHERS'))

t = Card('Prince', 'Princes', 'a Prince', 8, 0, 'c4c0b4', 'a4863c', prince_action)
standardCards.append(t)

# 457: Sauna
t = Card('Sauna', 'Saunas', 'a Sauna', 5, 0, 'c4c0b4', '9f8d7b', empty)
standardCards.append(t)

# 458: Stash
t = Card('Stash', 'Stashes', 'a Stash', 5, 0, 'd8c280', '666666', empty)
standardCards.append(t)

# 459: Summon
def summon_action(cM, gS, exc, tExc, pers):
    if cM[0].predName() in ['BUY']:
        exc.append(standardException(['SET ASIDE'], 'SUPPLY', 'OTHERS'))

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
def newTurnAction(cM, gS, exc, tExc, pers):
    for i in range(2):
        gS[-1].coins[i] = 0
        gS[-1].coinsLower[i] = 0
    gS[-1].activePlayer = cM[0].player
    gS[-1].phase = 0


t = Pred("^Turn (?P<cards>.*) - (?P<player>.*)$", newTurnAction, "NEW TURN")
standardPreds.append(t)


def standardGains(source, destination='DISCARDS'):
    def out_function(cM, gS, exc, tExc, pers):
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
def buyAndGainAction(cM, gS, exc, tExc, pers):
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


def pred7Action(cM, gS, exc, tExc, pers):
    # Mining Village Bug
    if cM[0].items.primary() == 'Mining Village' and cM[0].indent == 0:
        gS[-1].move(cM[0].player, 'INPLAYS', 'TRASH', cM[0].items)
    else:
        gS[-1].move(cM[0].player, 'HANDS', 'TRASH', cM[0].items)

    # Market Square
    exc.append(standardException(['DISCARD'], 'HANDS', 'DISCARDS',
                                 ['Market Square']))


# 7 Trashing
t = Pred("^(?P<player>.*) trashes (?P<cards>.*)\.$", pred7Action, "TRASH")
standardPreds.append(t)


def pred8Action(cM, gS, exc, tExc, pers):
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
def pred11Action(cM, gS, exc, tExc, pers):
    gS[-1].move(cM[0].player, 'HANDS', 'INPLAYS', cM[0].items)

t = Pred("^(?P<player>.*) plays (?P<cards>.*)\.$", pred11Action, "PLAY")
standardPreds.append(t)

# 12
def pred12Action(cM, gS, exc, tExc, pers):
    if cM[0].indent == 0:
        # Probably Scheme (or walled village / alch / treasury)
        gS[-1].move(cM[0].player, 'INPLAYS', 'DECKS', cM[0].items)

    else:
        gS[-1].move(cM[0].player, 'HANDS', 'DECKS', cM[0].items)

t = Pred("^(?P<player>.*) topdecks (?P<cards>.*)\.$", pred12Action, "TOPDECK")
standardPreds.append(t)

# 13
def pred13Action(cM, gS, exc, tExc, pers):
    gS[-1].move(cM[0].player, 'DECKS', 'HANDS', cM[0].items)

t = Pred("^(?P<player>.*) draws (?P<cards>.*) \(Wharf\)\.$", pred13Action, "WHARF DRAW")
standardPreds.append(t)

# 14
def pred14Action(cM, gS, exc, tExc, pers):
    gS[-1].move(cM[0].player, 'DECKS', 'HANDS', cM[0].items)

t = Pred("^(?P<player>.*) draws (?P<cards>.*) \(Hireling\)\.$", pred14Action, "HIRELING DRAW")
standardPreds.append(t)

# 15
def pred15Action(cM, gS, exc, tExc, pers):
    gS[-1].move(cM[0].player, 'DECKS', 'HANDS', cM[0].items)

t = Pred("^(?P<player>.*) draws (?P<cards>.*) \(Enchantress\)\.$", pred15Action, "WOODS DRAW")
standardPreds.append(t)

# 16
def pred16Action(cM, gS, exc, tExc, pers):
    gS[-1].move(cM[0].player, 'DECKS', 'HANDS', cM[0].items)

t = Pred("^(?P<player>.*) draws (?P<cards>.*) \(Haunted Woods\)\.$", pred16Action, "ENCHANTRESS DRAW")
standardPreds.append(t)

# 17
def pred17Action(cM, gS, exc, tExc, pers):
    gS[-1].move(cM[0].player, 'DECKS', 'HANDS', cM[0].items)

t = Pred("^(?P<player>.*) draws (?P<cards>.*) \(Caravan\)\.$", pred17Action, "CARAVAN DRAW")
standardPreds.append(t)

# 18
def pred18Action(cM, gS, exc, tExc, pers):
    gS[-1].move(cM[0].player, 'DECKS', 'HANDS', cM[0].items)

t = Pred("^(?P<player>.*) gets \+1 Buy, \+1 Action and draws (?P<cards>.*) \(Tactician\)\.$", pred18Action, "TACTICIAN DRAW")
standardPreds.append(t)

# 19
def pred19Action(cM, gS, exc, tExc, pers):
    gS[-1].move(cM[0].player, 'DECKS', 'HANDS', cM[0].items)

t = Pred("^(?P<player>.*) draws (?P<cards>.*) \(from (.*)\)$", pred19Action, "DRAW FROM")
standardPreds.append(t)

# 20
def pred20Action(cM, gS, exc, tExc, pers):
    gS[-1].move(cM[0].player, 'DECKS', 'HANDS', cM[0].items)

t = Pred("^(?P<player>.*) draws (?P<cards>.*) \(Ghost Town\)\.$", pred20Action, "GT DRAW")
standardPreds.append(t)

# 21
def pred21Action(cM, gS, exc, tExc, pers):
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
def pred25Action(cM, gS, exc, tExc, pers):
    if cM[0].indent == 0 and cM[0].items.primary() == 'Faithful Hound':
        gS[-1].move(cM[0].player, 'OTHERS', 'HANDS', cM[0].items)
    else:
        # Villa's handled somewhere else
        if cM[0].items.primary() != 'Villa':
            gS[-1].move(cM[0].player, 'DECKS', 'HANDS', cM[0].items)

t = Pred("^(?P<player>.*) puts (?P<cards>.*) into their hand\.$", pred25Action, "PUT INHAND")
standardPreds.append(t)

# 26
def pred26Action(cM, gS, exc, tExc, pers):
    if cM[0].items.primary() not in BOONHEX:
        gS[-1].move(cM[0].player, 'INPLAYS', 'OTHERS', cM[0].items)

t = Pred("^(?P<player>.*) sets (?P<cards>.*) aside\.$", pred26Action, "SET ASIDE")
standardPreds.append(t)

# 27
def pred27Action(cM, gS, exc, tExc, pers):
    gS[-1].move(cM[0].player, 'HANDS', 'OTHERS', cM[0].items)

t = Pred("^(?P<player>.*) puts (?P<cards>.*) on their (.*)\.$", pred27Action, "PUT ONTO")
standardPreds.append(t)

# 28
def pred28Action(cM, gS, exc, tExc, pers):
    gS[-1].move(cM[0].player, 'OTHERS', 'INPLAYS', cM[0].items)

t = Pred("^(?P<player>.*) calls (?P<cards>.*)\.$", pred28Action, "CALL")
standardPreds.append(t)

# 29
def pred29Action(cM, gS, exc, tExc, pers):
    gS[-1].move(cM[0].player, 'DECKS', 'DISCARDS', gS[-1].DECKS[cM[0].player])

t = Pred("^(?P<player>.*) moves their deck to the discard\.$", pred29Action, "DISCARD DECK")
standardPreds.append(t)

# 30
t = Pred("^(?P<player>.*) puts (?P<cards>.*) back onto their deck\.$", empty, "RETURN TOPDECK")
standardPreds.append(t)

# 31
def pred31Action(cM, gS, exc, tExc, pers):
    gS[-1].move(cM[0].player, 'DISCARDS', 'DECKS', cM[0].items)

t = Pred("^(?P<player>.*) shuffles (?P<cards>.*) into their deck\.$", pred31Action, "SHUFFLE INTO")
standardPreds.append(t)

# 32
t = Pred("^(?P<player>.*) inserts (?P<cards>.*) into their deck\.$", empty, "INSERT INTO")
standardPreds.append(t)

# 33
def pred33Action(cM, gS, exc, tExc, pers):
    gS[-1].move(cM[0].player, 'INPLAYS', 'SUPPLY', cM[0].items)

t = Pred("^(?P<player>.*) returns (?P<cards>.*) to (.*)\.$", pred33Action, "RETURN TO")
standardPreds.append(t)

# 34
t = Pred("^(?P<player>.*) returns (?P<cards>.*) set by (.*)\.$", empty, "RETURN SETBY")
standardPreds.append(t)

# 35
def pred35Action(cM, gS, exc, tExc, pers):
    gS[-1].move(cM[0].player, 'HANDS', 'SUPPLY', cM[0].items)

t = Pred("^(?P<player>.*) returns (?P<cards>.*)\.$", pred35Action, "RETURN")
standardPreds.append(t)

# 36
def pred36Action(cM, gS, exc, tExc, pers):
    gS[-1].move(cM[0].player, 'SUPPLY', 'DISCARDS', cM[0].items)

t = Pred("^(?P<player>.*) receives (?P<cards>.*)\.$", pred36Action, "RECEIVE.")
standardPreds.append(t)


# 37
def standard_boonhex(cM, gS, exc, tExc, pers):
    whichBoon = cM[0].items.primary()

    def removeBoonhex(exceptions):
        def out_function(cM, gS, exc, tExc, pers):
            for exception in exceptions:
                if exception in tExc:
                    tExc.remove(exception)
        return out_function

    def discardBoonhexCondition(cM):
        return cM[0].items.primary() == whichBoon and cM[0].predName() == 'DISCARD'

    elevated_topdeck = Exception(standardCondition(['TOPDECK']),
                                 moveException('DECKS', 'DECKS'),
                                 priority=1)
    elevated_trash = Exception(standardCondition(['TRASH']),
                               moveException('DECKS', 'TRASH'),
                               priority=1)
    elevated_harbinger = Exception(standardCondition(['TOPDECK']),
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
        greed_gain = standardException(['GAIN'], 'SUPPLY', 'DECKS', ['Copper'])
        copperStack = Cardstack({standardNames.index('Copper'): 1})
        greed_ongain = Exception(standardCondition(['GAIN'], ['Copper']),
                                 standardOnGains('DECKS'))
        tExc.append(greed_gain)
        tExc.append(greed_ongain)
        tExc.append(Exception(discardBoonhexCondition,
                    removeBoonhex([greed_ongain, greed_gain])))

    elif whichBoon == 'Plague':
        plague_gain = standardException(['GAIN'], 'SUPPLY', 'HANDS', ['Curse'])
        curseStack = Cardstack({standardNames.index('Curse'): 1})
        plague_ongain = Exception(standardCondition(['GAIN'], ['Copper']),
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
        famine_discard = standardException(['SHUFFLE INTO'], 'DECKS', 'DECKS')
        tExc.append(famine_discard)
        tExc.append(Exception(discardBoonhexCondition,
                    removeBoonhex([exc_revealDiscard, famine_discard])))


t = Pred("^(?P<player>.*) receives (?P<cards>.*)$", standard_boonhex, "RECEIVE BOONHEX")
standardPreds.append(t)


# 38
def passAction(cM, gS, exc, tExc, pers):
    gS[-1].HANDS[cM[0].player] -= cM[0].items
    gS[-1].HANDS[1 - cM[0].player] += cM[0].items


t = Pred("^(?P<player>.*) passes (?P<cards>.*) to (.*)\.$", passAction, "PASS")
standardPreds.append(t)


# 39
def pred39Action(cM, gS, exc, tExc, pers):
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
def buyAction(cM, gS, exc, tExc, pers):
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
def pred46Action(cM, gS, exc, tExc, pers):
    activePlayer = cM[0].player
    # Cleanup
    if cM[0].isCleanup:
        gS[-1].move(activePlayer, 'INPLAYS', 'DISCARDS', gS[-1].INPLAYS[activePlayer])
        gS[-1].move(activePlayer, 'HANDS', 'DISCARDS', gS[-1].HANDS[activePlayer])

    gS[-1].move(activePlayer, 'DISCARDS', 'DECKS', gS[-1].DISCARDS[activePlayer])

t = Pred("^(?P<player>.*) shuffles their deck\.$", pred46Action, "SHUFFLE")
standardPreds.append(t)

# 47
def pred47Action(cM, gS, exc, tExc, pers):
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
def pred62Action(cM, gS, exc, tExc, pers):
    gS[-1].move(cM[0].player, 'OTHERS', 'HANDS', cM[0].items)


t = Pred("^(?P<player>.*) puts (?P<cards>.*) in hand \(Gear\)\.$", pred62Action, "DRAW GEAR")
standardPreds.append(t)


# 63
def pred63Action(cM, gS, exc, tExc, pers):
    gS[-1].move(cM[0].player, 'OTHERS', 'HANDS', cM[0].items)


t = Pred("^(?P<player>.*) puts (?P<cards>.*) in hand \(Haven\)\.$", pred63Action, "DRAW HAVEN")
standardPreds.append(t)


# 64
def pred64Action(cM, gS, exc, tExc, pers):
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
def turn_start_action(cM, gS, exc, tExc, pers):
    exc.append(standardException(['PLAY'], 'OTHERS', 'INPLAYS'))
    exc.append(Exception(standardCondition(['PLAY']), standardOnPlay))
    exc.append(standardException(['PUT INHAND'], 'OTHERS', 'HANDS',
                                 ['Horse Traders']))

    # Probably Cobbler
    def immediate_gain_condition(cM):
        # Amulet!
        isSilver = cM[0].items.primary() == 'Silver'
        return cM[0].predName() == 'GAIN' and cM[0].indent == 1 and not isSilver

    whichBoon = cM[0].items.primary()

    # Boons and Shit
    def add_stuff(cM, gS, exc, tExc, pers):
        thisBoon = cM[0].items.primary()
        exc_gainNormally = Exception(standardCondition(['GAIN']),
                                     moveException('SUPPLY', 'DISCARDS'),
                                     priority=1)
        exc_onGainNormally = Exception(standardCondition(['GAIN']),
                                       standardOnGains('DISCARDS'),
                                       priority=1)

        def discardBoonhexCondition(cM):
            return cM[0].items.primary() == thisBoon and cM[0].predName() == 'DISCARD'

        def remove_stuff(exceptions):
            def out_function(cM, gS, exc, tExc, pers):
                for exception in exceptions:
                    if exception in tExc:
                        tExc.remove(exception)
            return out_function

        tExc.append(exc_gainNormally)
        tExc.append(exc_onGainNormally)
        tExc.append(Exception(discardBoonhexCondition,
                    remove_stuff([exc_gainNormally, exc_onGainNormally])))

    exc.append(Exception(standardCondition(['TAKES BOONHEX']), add_stuff))
    exc.append(Exception(immediate_gain_condition, moveException('SUPPLY', 'HANDS')))
    exc.append(Exception(immediate_gain_condition, standardOnGains('DECKS')))


t = Pred("^(?P<player>.*) starts their turn\.$", turn_start_action, "TURN START")
standardPreds.append(t)


# 73
def generic_vp_action(cM, gS, exc, tExc, pers):
    gS[-1].vps[cM[0].player] += int(cM[0].items[ARGUMENT_CARD].split('/')[0])


t = Pred("^(?P<player>.*) takes (?P<cards>.*) VP from (.*)\.$", generic_vp_action, "SHIELD GAIN")
standardPreds.append(t)

# 74
t = Pred("^(?P<player>.*) moves (?P<cards>.*) VP from (.*) to (.*)\.$", empty, "SHIELD MOVE")
standardPreds.append(t)


# 75
def obelisk_choice(cM, gS, exc, tExc, pers):
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
def setAsideWith_action(cM, gS, exc, tExc, pers):
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
def pred113Action(cM, gS, exc, tExc, pers):
    gS[-1].move(cM[0].player, 'SUPPLY', 'OTHERS', cM[0].items)
    gS[-1].INHERITED_CARDS[cM[0].player] = cM[0].items.cardList()[0]


t = Pred("^(?P<player>.*) inherits (?P<cards>.*)\.$", pred113Action, "INHERIT")
standardPreds.append(t)

# 114
t = Pred("^(?P<player>.*) fails to discard for The Sky's Gift$", empty, "SKY GIFT FAIL")
standardPreds.append(t)

# 115
def predCryptAction(cM, gS, exc, tExc, pers):
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
def predDonateAction(cM, gS, exc, tExc, pers):
    def moveEverything(cM, gS, exc, tExc, pers):
        gS[-1].move(cM[0].player, 'DECKS', 'HANDS',
                            gS[-1].DECKS[cM[0].player])
        gS[-1].move(cM[0].player, 'DISCARDS', 'HANDS',
                            gS[-1].DISCARDS[cM[0].player])

    def shuffleBack(cM, gS, exc, tExc, pers):
        gS[-1].move(cM[0].player, 'HANDS', 'DECKS',
                            gS[-1].HANDS[cM[0].player])

    exc.append(Exception(standardCondition(['PUT INHAND']), moveEverything))
    exc.append(Exception(standardCondition(['SHUFFLE INTO']), shuffleBack))


t = Pred("^Between Turns$", predDonateAction, "BETWEEN TURNS")
standardPreds.append(t)

# Last - catchall
t = Pred("^(.*)$", empty, "OTHERS")
standardPreds.append(t)


def urchin_trash_condition(cM):
    out = 0
    for index in range(1, len(cM)-1):
        if standardCondition(['TRASH'], ['Urchin'])(cM[index]) and out == 0:
            out = 1

        if standardCondition(['GAIN'], ['Mercenary'])(cM[index + 1]) and out == 1:
            out = 2
    return out == 2


def urchin_trash_exception(cM, gS, exc, tExc, pers):
    standardPreds[cM[0].pred].action(cM, gS, exc, tExc, pers)
    standardOnPlay(cM, gS, exc, tExc, pers)

    exc.append(Exception(standardCondition(['TRASH'], ['Urchin']),
                         moveException('INPLAYS', 'TRASH'),
                         priority=1))


def hermit_trash_condition(cM):
    out = 0
    for index in range(1, len(cM)-1):
        if standardCondition(['TRASH'], ['Hermit'])(cM[index]) and out == 0:
            out = 1

        if standardCondition(['GAIN'], ['Madman'])(cM[index + 1]) and out == 1:
            out = 2
    return out == 2


def hermit_trash_exception(cM, gS, exc, tExc, pers):
    standardPreds[cM[0].pred].action(cM, gS, exc, tExc, pers)
    standardOnPlay(cM, gS, exc, tExc, pers)

    exc.append(Exception(standardCondition(['TRASH'], ['Hermit']),
                         moveException('INPLAYS', 'TRASH'),
                         priority=1))


standardPersistents.append(Exception(urchin_trash_condition, urchin_trash_exception))
standardPersistents.append(Exception(hermit_trash_condition, hermit_trash_exception))
standardPersistents.append(standardException(['RETURN TO'], 'OTHERS', 'SUPPLY',
                                             ['Encampment']))
travellers = ['Page', 'Treasure Hunter', 'Warrior', 'Hero', 'Champion', 'Peasant', 'Soldier', 'Fugitive', 'Disciple', 'Teacher']
standardPersistents.append(standardException(['RETURN'], 'INPLAYS', 'SUPPLY',
                                             travellers))
standardPersistents.append(Exception(standardCondition(['DISCARD'], ['Wine Merchant']),
                                     moveException('OTHERS', 'DISCARDS')))

standardNames = [x.simple_name for x in standardCards]
