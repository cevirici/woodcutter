from .classes import *
from .Cardstack import *


def gardens_worth(state, player):
    return len(state.crunch(GameState.playerZones, [player])) // 10


def duke_worth(state, player):
    return state.crunch(GameState.playerZones, [player])['DUCHY']


def vineyard_worth(state, player):
    playerDeck = state.crunch(GameState.playerZones, [player])
    estates = playerDeck['ESTATE'] if state.inherited[player] != 'NOTHING' \
        else 0
    return (sum([playerDeck[item] for item in playerDeck if
                 'a' in Cards[item].types]) + estates) // 3


def fairgrounds_worth(state, player):
    playerDeck = state.crunch(GameState.playerZones, [player])
    return len(playerDeck.cardList()) // 5


def silkroad_worth(state, player):
    playerDeck = state.crunch(GameState.playerZones, [player])
    return sum([playerDeck[item] for item in playerDeck if
                'v' in Cards[item].types]) // 4


def feodum_worth(state, player):
    return state.crunch(GameState.playerZones, [player])['SILVER'] // 3


def distantlands_worth(state, player):
    playerDeck = state.crunch(GameState.playerZones, [player])
    return state['OTHERS'][player]['DISTANT LANDS'] / \
        playerDeck['DISTANT LANDS']


def humblecastle_worth(state, player):
    playerDeck = state.crunch(GameState.playerZones, [player])
    return sum([playerDeck[item] for item in playerDeck if
                'c' in Cards[item].types])


def kingscastle_worth(state, player):
    playerDeck = state.crunch(GameState.playerZones, [player])
    return sum([playerDeck[item] for item in playerDeck if
                'c' in Cards[item].types]) * 2


def banditfort_worth(state, player):
    playerDeck = state.crunch(GameState.playerZones, [player])
    return playerDeck['SILVER'] + playerDeck['GOLD'] * -3


def fountain_worth(state, player):
    playerDeck = state.crunch(GameState.playerZones, [player])
    return 15 if playerDeck['COPPER'] >= 10 else 0


def keep_worth(state, player):
    playerDeck = state.crunch(GameState.playerZones, [player])
    otherDeck = state.crunch(GameState.playerZones, [1 - player])

    return 5 * len([card for card in playerDeck if 't' in Cards[card].types and
                    playerDeck[card] >= otherDeck[card]])


def museum_worth(state, player):
    playerDeck = state.crunch(GameState.playerZones, [player])
    return len(playerDeck.cardList()) * 2


def obelisk_worth(state, player):
    playerDeck = state.crunch(GameState.playerZones, [player])
    return sum([playerDeck[card] for card in playerDeck
                if card in state.obelisk])


def orchard_worth(state, player):
    playerDeck = state.crunch(GameState.playerZones, [player])
    estates = 4 if state.inherited[player] != 'NOTHING' and\
        playerDeck['ESTATE'] >= 3 else 0
    return len([item for item in playerDeck if
                'a' in Cards[item].types and
                playerDeck[item] >= 3]) * 4 + estates


def palace_worth(state, player):
    playerDeck = state.crunch(GameState.playerZones, [player])
    return min([playerDeck[item] for item in ['COPPER', 'SILVER', 'GOLD']]) * 3


def tower_worth(state, player):
    def card_worth(card, state):
        pairs = [['ENCAMPMENT', 'PLUNDER'],
                 ['PATRICIAN', 'EMPORIUM'],
                 ['SETTLERS', 'BUSTLING VILLAGE'],
                 ['CATAPULT', 'ROCKS'],
                 ['GLADIATOR', 'FORTUNE'],
                 ['DAME ANNA', 'DAME JOSEPHINE', 'DAME MOLLY', 'DAME NATALIE',
                  'DAME SYLVIA', 'SIR BAILEY', 'SIR DESTRY', 'SIR MARTIN',
                  'SIR MICHAEL', 'SIR VANDER'],
                 ['RUINED LIBRARY', 'RUINED VILLAGE', 'ABANDONED MINE',
                  'RUINED MARKET', 'SURVIVORS'],
                 ['SAUNA', 'AVANTO']]

        if 'v' not in Cards[card].types or card == 'DAME JOSEPHINE':
            for pair in pairs:
                if card in pair:
                    for others in pair:
                        if others in state['SUPPLY']:
                            return 0
                    return 1
            if card in state['SUPPLY']:
                return 0
            else:
                return 1
        else:
            return 0

    playerDeck = state.crunch(GameState.playerZones, [player])
    return sum([card_worth(card, state) * playerDeck[card]
                for card in playerDeck])


def arch_worth(state, player):
    playerDeck = state.crunch(GameState.playerZones, [player])
    estates = state.inherited[player] != 'NOTHING'
    best, second = (0, 0)
    for card in playerDeck:
        if 'a' in Cards[card].types or (estates and card == 'ESTATE'):
            amount = playerDeck[card]
            if amount > best:
                second, best = best, amount
            elif amount > second:
                second = amount

    return 3 * second


def wall_worth(state, player):
    playerDeck = state.crunch(GameState.playerZones, [player])
    return min(0, 15 - len(playerDeck))


def den_worth(state, player):
    playerDeck = state.crunch(GameState.playerZones, [player])
    return -3 * len([card for card in playerDeck if playerDeck[card] == 1])


def pasture_worth(state, player):
    return state.crunch(GameState.playerZones, [player])['ESTATE']


d = {'GARDENS': gardens_worth,
     'DUKE': duke_worth,
     'VINEYARD': vineyard_worth,
     'SILK ROAD': silkroad_worth,
     'FEODUM': feodum_worth,
     'DISTANT LANDS': distantlands_worth,
     'HUMBLE CASTLE': humblecastle_worth,
     "KING'S CASTLE": kingscastle_worth,
     'BANDIT FORT': banditfort_worth,
     'FOUNTAIN': fountain_worth,
     'KEEP': keep_worth,
     'MUSEUM': museum_worth,
     'OBELISK': obelisk_worth,
     'ORCHARD': orchard_worth,
     'PALACE': palace_worth,
     'TOWER': tower_worth,
     'TRIUMPHAL ARCH': arch_worth,
     'WALL': wall_worth,
     "WOLF DEN": den_worth,
     'PASTURE': pasture_worth}

for card in d:
    Cards[card].worth = d[card]
