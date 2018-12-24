from .lists import *
from .Card import *
from .Pred import *
from .Cardstack import *
from .Exception import *
from copy import deepcopy


PLAY_PREDS = ('PLAY', 'THRONE', 'KING', 'THRONE GENERIC',
              'PLAY COIN', 'THRONE COIN')
GAIN_PREDS = ('GAIN', 'BUY AND GAIN', 'GAIN TOPDECK', 'GAIN TRASH',
              'GAIN EXPERIMENT')


def findRemainingSteps(i, moves):
    for c in range(len(moves) - i):
        if str(moves[c + i].pred) == "NEW TURN":
            return c
    return len(moves) - i


# -- Standard Exceptions -- #

def always(move):
    return True


def default_action(moves, i, blockLength, state):
    moves[i].pred.action(moves, i, blockLength, state)


defaultMove = Exception(always, default_action, -1, [], 0, True)


def check(predList, targetList=[]):
    def out_function(move):
        if predList:
            if move.pred not in predList:
                return False

        if targetList:
            if len([t for t in targetList if (t in move.items[0])]) == 0:
                return False
        return True

    return out_function


def transfer(src, dest, move, cS):
    if len(move.items) > 0:
        cS.move(move.player, src, dest, move.items)
    return {}


def moveFunct(src, dest):
    def out_function(moves, i, blockLength, state):
        state.move(moves[i].player, src, dest, moves[i].items[0])
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


exc_revealTopdeck = checkMove(['TOPDECK'], 'DECKS', 'DECKS')
exc_revealDiscard = checkMove(['DISCARD'], 'DECKS', 'DISCARDS')
exc_harbinger = checkMove(['TOPDECK'], 'DISCARDS', 'DECKS')
exc_gainHand = checkMove(['GAIN'], 'SUPPLY', 'HANDS')


def standard_trash(source):
    def out_function(moves, i, blockLength, state):
        move = moves[i]
        state.move(move.player, source, 'TRASH', move.items[0])
    return out_function


exc_revealTrash = Exception(check(['TRASH']), standard_trash('DECKS'))
exc_supplyTrash = Exception(check(['TRASH']), standard_trash('SUPPLY'))
exc_inplayTrash = Exception(check(['TRASH']), standard_trash('INPLAYS'))


def gainTo(source, destination):
    return Exception(check(['GAIN']), standard_gains(source, destination))


# --- Individual Cards --- #

# -- Base -- #

# -- PREDS -- #


def new_turn_action(moves, i, blockLength, state):
    state.activePlayer = moves[i].player
    state.phase = 0
    state.coins = 0
    state.actions = 1
    state.buys = 1

    newDurations = []
    for stack, life in state.durations[moves[i].player]:
        if life != 1:
            if life > 1:
                life -= 1
            newDurations.append((stack, life))
    state.durations[moves[i].player] = newDurations


Preds['NEW TURN'].action = new_turn_action


def turn_start_action(moves, i, blockLength, state):
    state.phase = 0


Preds['TURN START'].action = turn_start_action


def predDonateAction(moves, i, blockLength, state):
    def moveEverything(moves, i, blockLength, state):
        move = moves[i]
        state.move(move.player, 'DECKS', 'HANDS',
                   state['DECKS'][move.player])
        state.move(move.player, 'DISCARDS', 'HANDS',
                   state['DISCARDS'][move.player])

    def shuffleBack(moves, i, blockLength, state):
        state.move(moves[i].player, 'HANDS', 'DECKS',
                   state['HANDS'][moves[i].player])

    putExc = Exception(check(['PUT INHAND']), moveEverything)
    shuffleExc = Exception(check(['SHUFFLE INTO']), shuffleBack)
    for exc in [putExc, shuffleExc]:
        newExc = deepcopy(exc)
        newExc.lifespan = blockLength
        newExc.indents = [moves[i].indent + 1]
        state.exceptions.add(newExc)


Preds['BETWEEN TURNS'].action = predDonateAction

Preds['STARTS'].action = moveFunct('SUPPLY', 'DECKS')


def get_gain_dest(card):
    alts = {'NOMAD CAMP': 'DECKS',
            'DEN OF SIN': 'HANDS',
            'GUARDIAN': 'HANDS',
            'GHOST TOWN': 'HANDS',
            'NIGHT WATCHMAN': 'HANDS'}

    if card in alts:
        return alts[card]
    else:
        return 'DISCARDS'


def standard_gains(source, destination='DISCARDS'):
    def out_function(moves, i, blockLength, state):
        move = moves[i]
        targetStuff = deepcopy(move.items[0])

        # If default, check for exceptional gain destinations
        if destination == 'DISCARDS':
            for card in targetStuff:
                block = Cardstack({card: targetStuff[card]})
                state.move(move.player, source, get_gain_dest(card), block)
        else:
            state.move(move.player, source, destination, targetStuff)

    return out_function


def buy_and_gain(moves, i, blockLength, state):
    standard_gains('SUPPLY')(moves, i, blockLength, state)
    if moves[i].indent == 0:
        state.phase = 2


def gain_experiment(moves, i, blockLength, state):
    state.move(moves[i].player, 'SUPPLY', 'DECKS',
               Cardstack({'EXPERIMENT': 1}))


Preds['BUY AND GAIN'].action = buy_and_gain
Preds['GAIN TOPDECK'].action = standard_gains('SUPPLY', 'DECKS')
Preds['GAIN TRASH'].action = standard_gains('TRASH')
Preds['GAIN EXPERIMENT'].action = gain_experiment
Preds['GAIN'].action = standard_gains('SUPPLY')


def buy_action(moves, i, blockLength, state):
    move = moves[i]
    target = move.items[0].primary

    if move.indent == 0:
        state.phase = 2
        state.buys -= 1

    if target == 'MINT':
        newExc = deepcopy(exc_inplayTrash)
        newExc.lifespan = blockLength
        newExc.indents = [moves[i].indent + 1]
        state.exceptions.add(newExc)


Preds['BUY'].action = buy_action
Preds['TRASH'].action = standard_trash('HANDS')


def discard_action(moves, i, blockLength, state):
    move = moves[i]
    state.move(move.player, 'HANDS', 'DISCARDS', move.items[0])


Preds['DISCARD'].action = discard_action


def get_stayout_duration(moves, i):
    move = moves[i]
    target = move.items[0].primary
    if target in ['CARAVAN', 'FISHING VILLAGE', 'LIGHTHOUSE', 'MERCHANT SHIP',
                  'WHARF']:
        return 1

    elif target in ['HAVEN', 'GEAR']:
        j = i + 1
        while j < len(moves) and moves[j].indent > moves[i].indent:
            secondary = moves[j]
            if secondary.indent == move.indent + 1 and \
                    secondary.pred == 'SET ASIDE WITH':
                return 1
            j += 1
    elif target == 'OUTPOST':
        j = i + 1
        while j < len(moves) and moves[j].indent > moves[i].indent:
            if moves[j].pred in ['OUTPOST FAIL', 'OUTPOST FAIL2']:
                return 0
            j += 1
        return 1


def standard_plays(moves, i, blockLength, state):
    def move_play(source, dest='INPLAYS'):
        def out_function(moves, i, blockLength, state):
            state.move(moves[i].player, source, dest, moves[i].items[0])
            play_setout(moves, i, blockLength, state)
        return out_function

    move = moves[i]
    target = move.items[0].primary
    triggers = {'ARTISAN': [gainTo('SUPPLY', 'HANDS')],
                'BANDIT': [exc_revealTrash, exc_revealDiscard],
                'BUREAUCRAT': [gainTo('SUPPLY', 'DECKS')],
                'HARBINGER': [exc_harbinger],
                'LIBRARY': [checkMove(['SETS ASIDE WITH'], 'HANDS', 'OTHERS'),
                            checkMove(['DISCARD'], 'OTHERS', 'DISCARDS')],
                'MINE': [gainTo('SUPPLY', 'HANDS')],
                'SENTRY': [exc_revealTrash, exc_revealDiscard,
                           exc_revealTopdeck],
                'VASSAL': [exc_revealDiscard,
                           Exception(check(['PLAY']), move_play('DISCARDS'))],
                'LURKER': [exc_supplyTrash, gainTo('TRASH', 'DISCARDS')],
                'MINING VILLAGE': [exc_inplayTrash],
                'PATROL': [exc_revealTopdeck],
                'SWINDLER': [exc_revealTrash],
                'TORTURER': [gainTo('SUPPLY', 'HANDS')],
                'TRADING POST': [gainTo('SUPPLY', 'HANDS')],
                'EMBARGO': [exc_inplayTrash],
                'EXPLORER': [gainTo('SUPPLY', 'HANDS')],
                'AMBASSADOR': [checkMove(['RETURN TO'], 'HANDS', 'SUPPLY')],
                'ISLAND': [checkMove(['PUT ONTO'], 'INPLAYS', 'OTHERS')],
                'LOOKOUT': [exc_revealTrash, exc_revealDiscard,
                            exc_revealTopdeck],
                'NATIVE VILLAGE': [checkMove(['SET ASIDE WITH'],
                                             'DECKS', 'OTHERS'),
                                   checkMove(['PUT INHAND'],
                                             'OTHERS', 'HANDS')],
                'NAVIGATOR': [exc_revealTopdeck, exc_revealDiscard],
                'PEARL DIVER': [exc_revealTopdeck,
                                checkMove(['BOTTOMDECK'], 'DECKS', 'DECKS')],
                'PIRATE SHIP': [exc_revealTrash, exc_revealDiscard],
                'SEA HAG': [exc_revealDiscard, gainTo('SUPPLY', 'DECKS')],
                'TREASURE MAP': [exc_inplayTrash],
                'APOTHECARY': [exc_revealTopdeck],
                'GOLEM': [Exception(check(['REVEAL']),
                                    moveFunct('DECKS', 'OTHERS'),
                                    persistent=True),
                          Exception(check(['PLAY']), move_play('OTHERS'),
                                    persistent=True),
                          checkMove(['DISCARD'], 'OTHERS', 'DISCARDS')],
                'SCRYING POOL': [exc_revealTopdeck, exc_revealDiscard],
                'LOAN': [exc_revealDiscard, exc_revealTrash],
                'VENTURE': [exc_revealDiscard, move_play('DECKS')]
                }

    if target in triggers:
        for exc in triggers[target]:
            newExc = deepcopy(exc)
            newExc.lifespan = blockLength
            newExc.indents = [moves[i].indent + 1]
            state.exceptions.add(newExc)

    if target == 'REPLACE':
        for move in moves[i + 1: i + blockLength]:
            if move.pred == 'GAIN':
                target = move.items[0]

                def replace_topdeck(moves, i, blockLength, state):
                    state.move(moves[i].player, get_gain_dest(target.primary),
                               'DECKS', target)

                newExc = Exception(check(['TOPDECK'],
                                         ['CARD', target.primary]),
                                   replace_topdeck)
                newExc.lifespan = blockLength
                newExc.indents = [move.indent + 1]
                state.exceptions.add(newExc)
                break

    if target in ['THRONE ROOM', "KING'S COURT", 'DISCIPLE', 'SCEPTER']:
        durations = []
        exceptions = [Exception(check(['PLAY', 'THRONE',
                                       'THRONE GENERIC', 'KING']),
                                standard_plays),
                      checkMove(['PLAY'], 'HANDS', 'INPLAYS')]
        for newExc in exceptions:
            newExc.lifespan = blockLength
            newExc.indents = [moves[i].indent + 1]
            state.exceptions.add(newExc)

        for j in range(i + 1, i + blockLength):
            if moves[j].indent == moves[i].indent + 1 and \
                    moves[j].pred in ['PLAY', 'THRONE',
                                      'THRONE GENERIC', 'KING']:
                subject = moves[j].items[0].primary
                stayout = get_stayout_duration(moves, j)
                if stayout:
                    durations.append(stayout)
        if durations:
            length = -1 if -1 in durations else max(durations)
            state.durations[move.player].append((Cardstack({subject: 1}),
                                                 length))
            state.durations[move.player].append((Cardstack({target: 1}),
                                                 length))


def play_setout(moves, i, blockLength, state):
    move = moves[i]
    target = move.items[0].primary
    standard_plays(moves, i, blockLength, state)

    # Durations
    stayout = get_stayout_duration(moves, i)
    if stayout:
        state.durations[move.player].append((Cardstack({target: 1}), stayout))


def play_action(moves, i, blockLength, state):
    target = Cards[moves[i].items[0].primary]

    if moves[i].indent == 0:
        # Set phase
        if 't' in target.types and 'a' not in target.types:
            state.phase = 2
        elif 'n' in target.types and 'a' not in target.types:
            state.phase = 3
        elif target == 'WEREWOLF':
            state.phase = 1
            if i < len(moves):
                if moves[i + 1].pred == 'TAKES BOONHEX':
                    state.phase = 3
        else:
            state.phase = 1

        if state.phase == 1:
            state.actions -= 1

    play_setout(moves, i, blockLength, state)

    state.move(moves[i].player, 'HANDS', 'INPLAYS', moves[i].items[0])


def play_coin_action(moves, i, blockLength, state):
    move = moves[i]
    state.coins += int(move.arguments[0])
    play_action(moves, i, blockLength, state)


Preds['PLAY'].action = play_action
Preds['PLAY COIN'].action = play_coin_action
Preds['THRONE'].action = standard_plays
Preds['KING'].action = standard_plays
Preds['THRONE COIN'].action = standard_plays
Preds['THRONE GENERIC'].action = standard_plays


def topdeck_action(moves, i, blockLength, state):
    move = moves[i]
    if state.phase == 4:
        # Probably Scheme (or walled village / alch / treasury)
        state.move(move.player, 'INPLAYS', 'DECKS', move.items[0])

    else:
        state.move(move.player, 'HANDS', 'DECKS', move.items[0])


Preds['TOPDECK'].action = topdeck_action
Preds['INSERT INTO'].action = moveFunct('HANDS', 'DECKS')
Preds['BOTTOMDECK'].action = moveFunct('HANDS', 'DECKS')


def draw_action(moves, i, blockLength, state):
    move = moves[i]
    player = move.player
    # Cleanup
    if state.phase == 4:
        if move.player == player:
            cleanable = state['INPLAYS'][player]
            for stack, life in state.durations[player]:
                cleanable -= stack
            state.move(player, 'INPLAYS', 'DISCARDS', cleanable)
            state.move(player, 'HANDS', 'DISCARDS', state['HANDS'][player])

    state.move(move.player, 'DECKS', 'HANDS', move.items[0])


Preds['DRAW'].action = draw_action
for p in ['DRAW GENERIC', 'TACTICIAN DRAW', 'DRAW FROM']:
    Preds[p].action = moveFunct('DECKS', 'HANDS')


def wish_action(moves, i, blockLength, state):
    move = moves[i]
    block = Cardstack({move.items[0].primary: 1})
    state.move(move.player, 'DECKS', 'HANDS', block)


Preds['WISH SUCCESS'].action = wish_action


def inhand_action(moves, i, blockLength, state):
    move = moves[i]
    if move.indent == 0 and move.items[0].primary == 'FAITHFUL HOUND':
        state.move(move.player, 'OTHERS', 'HANDS', move.items[0])
    else:
        state.move(move.player, 'DECKS', 'HANDS', move.items[0])


Preds['PUT INHAND'].action = inhand_action
Preds['INHAND GENERIC'].action = inhand_action


def set_aside_action(moves, i, blockLength, state):
    move = moves[i]
    if 'b' not in move.items[0].primary:
        state.move(move.player, 'INPLAYS', 'OTHERS', move.items[0])


Preds['SET ASIDE'].action = set_aside_action

Preds['PUT ONTO'].action = moveFunct('HANDS', 'OTHERS')


def call_action(moves, i, blockLength, state):
    move = moves[i]
    state.move(move.player, 'INPLAYS', 'OTHERS', move.items[0])
    # Barring some weird stuff like carriaging a werewolf/crown
    if move.indent == 0:
        state.phase = 1


Preds['CALL'].action = call_action


def deck_discard_action(moves, i, blockLength, state):
    state.move(moves[i].player, 'DECKS', 'DISCARDS',
               state['DECKS'][moves[i].player])


Preds['DISCARD DECK'].action = deck_discard_action
Preds['SHUFFLE INTO'].action = moveFunct('DISCARDS', 'DECKS')


def shuffle_action(moves, i, blockLength, state):
    player = moves[i].player
    # Cleanup
    if state.phase == 4:
        cleanable = state['INPLAYS'][player]
        for stack, life in state.durations[player]:
            cleanable -= stack
        state.move(player, 'INPLAYS', 'DISCARDS', cleanable)
        state.move(player, 'HANDS', 'DISCARDS', state['HANDS'][player])

    state.move(player, 'DISCARDS', 'DECKS', state['DISCARDS'][player])


Preds['SHUFFLE'].action = shuffle_action

Preds['RETURN TO'].action = moveFunct('INPLAYS', 'SUPPLY')
Preds['RETURN'].action = moveFunct('HANDS', 'SUPPLY')


def standard_boonhex(moves, i, blockLength, state):
    move = moves[i]
    whichBoon = move.items[0].primary()
    for index in range(i, len(moves) - i):
        if move[index].items.primary() == whichBoon and\
           str(move[index].pred) == 'DISCARD':
            break

    timeout = index + 1 - i

    if whichBoon == 'The Sun\'s Gift':
        state.exceptions.update({exc: timeout for exc in
                                 [exc_revealTopdeck, exc_revealDiscard]})

    elif whichBoon == 'The Moon\'s Gift':
        state.exceptions.update({exc_harbinger: timeout})

    elif whichBoon == 'Locusts':
        state.exceptions.update({exc_revealTrash: timeout})

    elif whichBoon == 'War':
        state.exceptions.update({exc: timeout for exc in
                                 [exc_revealTrash, exc_revealDiscard]})

    elif whichBoon == 'Greed':
        greed_gain = checkMove(['GAIN'], 'SUPPLY', 'DECKS', ['COPPER'])
        greed_ongain = Exception(check(['GAIN'], ['COPPER']),
                                 onGains('DECKS', Cardstack({'COPPER': 1})))
        state.exceptions.update({exc: timeout for exc in
                                 [greed_gain, greed_ongain]})

    elif whichBoon == 'Plague':
        plague_gain = checkMove(['GAIN'], 'SUPPLY', 'HANDS', ['CURSE'])
        plague_ongain = Exception(check(['GAIN'], ['CURSE']),
                                  onGains('DECKS', Cardstack({'CURSE': 1})))
        state.exceptions.update({exc: timeout for exc in
                                 [plague_gain, plague_ongain]})

    elif whichBoon == 'Bad Omens':
        state.exceptions.update({exc: timeout for exc in
                                 [exc_harbinger, exc_revealDiscard]})

    elif whichBoon == 'Famine':
        famine_discard = checkMove(['SHUFFLE INTO'], 'DECKS', 'DECKS')
        state.exceptions.update({exc: timeout for exc in
                                 [famine_discard, exc_revealDiscard]})


Preds['RECEIVE'].action = standard_boonhex


def pass_action(moves, i, blockLength, state):
    move = moves[i]
    state['HANDS'][move.player] -= move.items[0]
    state['HANDS'][1 - move.player] += move.items[0]


Preds['PASS'].action = pass_action


def genericVP(moves, i, blockLength, state):
    move = moves[i]
    cS.vps[move.player] += int(move.arguments[0])


for p in ['SHIELD GAIN', 'SHIELD GET', 'SHIELD GENERIC']:
    Preds[p].action = genericVP


Preds['SET ASIDE WITH'].action = moveFunct('HANDS', 'OTHERS')


def take_coffers(moves, i, blockLength, state):
    move = moves[i]
    state.coffers[move.player] += int(move.arguments[0])


Preds['COFFERS GENERIC'].action = take_coffers
Preds['COFFER GENERIC'].action = take_coffers
Preds['COFFERS FROM'].action = take_coffers
Preds['GAIN COFFERS'].action = take_coffers


def use_coffers(moves, i, blockLength, state):
    move = moves[i]
    state.coffers[move.player] -= int(move.arguments[0])
    state.coins += int(move.arguments[0])


Preds['USE COFFERS'].action = use_coffers
Preds['USE COFFER'].action = use_coffers


def take_debt(moves, i, blockLength, state):
    move = moves[i]
    state.debt[move.player] += int(move.arguments[0])


Preds['TAKE DEBT'].action = take_debt


def repay_debt(moves, i, blockLength, state):
    move = moves[i]
    state.debt[move.player] -= int(move.arguments[0])
    state.coins -= int(move.arguments[0])


Preds['REPAY DEBT'].action = repay_debt
Preds['REPAY DEBT PARTIAL'].action = repay_debt


def gain_coin(moves, i, blockLength, state):
    move = moves[i]
    state.coins += int(move.arguments[0])


Preds['COINS GENERIC'].action = gain_coin
Preds['GAIN COINS'].action = gain_coin
Preds['COIN TOKEN'].action = gain_coin


def lose_coin(moves, i, blockLength, state):
    move = moves[i]
    state.coins -= int(move.arguments[0])


Preds['LOSE COINS'].action = lose_coin
Preds['LOSE COIN'].action = lose_coin


def get_buy(moves, i, blockLength, state):
    move = moves[i]
    state.buys += int(move.arguments[0])


Preds['BUYS GENERIC'].action = get_buy
Preds['BUY GENERIC'].action = get_buy
Preds['GET BUYS'].action = get_buy
Preds['GET BUY'].action = get_buy


def get_action(moves, i, blockLength, state):
    move = moves[i]
    state.actions += int(move.arguments[0])


Preds['ACTIONS GENERIC'].action = get_action
Preds['ACTION GENERIC'].action = get_action
Preds['ACTIONS'].action = get_action
Preds['ACTION'].action = get_action


def get_villager(moves, i, blockLength, state):
    move = moves[i]
    state.villagers[move.player] += int(move.arguments[0])


Preds['VILLAGERS GENERIC'].action = get_villager
Preds['VILLAGER GENERIC'].action = get_villager
Preds['GAIN VILLAGERS'].action = get_villager
Preds['GAIN VILLAGER'].action = get_villager


def use_villager(moves, i, blockLength, state):
    move = moves[i]
    state.villagers[move.player] -= int(move.arguments[0])
    state.actions -= int(move.arguments[0])


Preds['USE VILLAGERS'].action = use_villager
Preds['USE VILLAGER'].action = use_villager


def obelisk_choice(moves, i, blocklength, state):
    move = moves[i]
    target = move.items.primary()
    state.obelisk = [target]

    PAIRS = [['ENCAMPMENT', 'PLUNDER'],
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

    for pair in PAIRS:
        if target in pair:
            state.obelisk = pair
            return {}


def inherit_action(moves, i, blocklength, state):
    move = moves[i]
    state.move(move.player, 'SUPPLY', 'OTHERS', move.items[0])
    cS.inherited[move.player] = Cards[move.items.primary]


Preds['OBELISK CHOICE'].action = obelisk_choice
Preds['INHERIT'].action = inherit_action


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

INTRINSIC_EXCEPTIONS = [defaultMove]


# def estate_action(moves, i, blockLength, state):
#     state.inherited[moves[i].player].action(moves, i, blockLength, state)


# Cards['ESTATE'].action = estate_action


# def artisan_action(moves, i, blockLength, state):
#     if move.pred in PLAY_PREDS:
#         onGainExc = Exception(check(['GAIN']), onGains('HANDS'), 1)
#         state.exceptions[onGainExc] = blockLength[i]


# Cards['ARTISAN'].action = artisan_action

# Cards['BANDIT'].action = banditlike


# def bureaucrat_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         onGainExc = Exception(check(['GAIN']), onGains('DECKS'))
#         gainExc = checkMove(['GAIN'], 'SUPPLY', 'DECKS', ['Silver'])
#         return {exc: bL for exc in [onGainExc, gainExc]}


# Cards['BUREAUCRAT'].action = bureaucrat_action


# def gardens_worth(gS, player):
#     return gS.crunch(PERSONAL_ZONES, (player)).count() // 10


# Cards['GARDENS'].worth = gardens_worth

# Cards['HARBINGER'].action = harbingerlike


# def library_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         setAsideExc = checkMove(['SETS ASIDE WITH'], 'DECKS', 'OTHERS')
#         libDiscardExc = checkMove(['DISCARD'], 'OTHERS', 'DISCARDS')
#         return {exc: bL for exc in [setAsideExc, libDiscardExc]}


# Cards['LIBRARY'].action = library_action


# def mine_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         onGainExc = Exception(check(['GAIN']), onGains('HANDS'))
#         return {exc: bL for exc in [exc_gainHand, onGainExc]}


# Cards['MINE'].action = mine_action

# Cards['SENTRY'].action = sentrylike


# def vassal_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         outputExcs = {exc_revealDiscard: bL}

#         for scan in moves[i + 1: i + bL]:
#             if str(scan.pred) == 'DISCARD':
#                 discardedCard = str(scan.primary())
#                 vassalCheck = check(['PLAY'], [discardedCard])
#                 playExc = Exception(vassalCheck, move('DISCARDS', 'INPLAYS'))
#                 actionExc = Exception(vassalCheck, onPlay)
#                 outputExcs.update({playExc: bL, actionExc: bL})
#                 break

#         return outputExcs


# Cards['VASSAL'].action = vassal_action


# # 40: Diplomat
# def diplomat_action(move, i, bL, moves, cS):
#     if str(move.pred) in ['REACT']:
#         return {checkMove(['DISCARD'], 'HANDS', 'DISCARDS'): bL}


# Cards['DIPLOMAT'].action = diplomat_action


# def duke_worth(gS, player):
#     playerDeck = gS.crunch(PERSONAL_ZONES, (player))
#     return playerDeck['DUCHY']


# Cards['DUKE'].worth = duke_worth


# def lurker_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         return {exc: bL for exc in [exc_supplyTrash,
#                                     exc_standardTrash,
#                                     checkMove(['GAIN'], 'TRASH', 'DISCARDS'),
#                                     Exception(check(['GAIN']),
#                                               onGains('DISCARDS'))
#                                     ]}


# Cards['LURKER'].action = lurker_action


# def mv_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         def delayedTrashCondition(move):
#             return move.indent == 0 and \
#                 str(move.pred) == 'TRASH' and \
#                 move.items.primary() == 'MINING VILLAGE'

#         trashExc = checkMove(['TRASH'], 'INPLAYS', 'TRASH', ['MINING VILLAGE'])
#         if move.indent == 0:
#             delayedTrash = Exception(delayedTrashCondition,
#                                      moveFunct('INPLAYS', 'TRASH'))
#             return {trashExc: bL, delayedTrash: bL + 1}
#         else:
#             return {trashExc: bL}


# Cards['MINING VILLAGE'].action = mv_action


# def patrol_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         return{exc_revealTopdeck: bL}


# Cards['PATROL'].action = patrol_action


# def replace_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         for scan in moves[i + 1: i + bL]:
#             if str(scan) == 'GAIN' and scan.player == move.player:
#                 gainedCard = scan.items.primary()
#                 gainedStack = Cardstack({gainedCard: 1})

#                 def topdeckGainedCard(move, i, bL, moves, cS):
#                     cS.move(move.player, 'DISCARDS', 'DECKS', gainedStack)

#                 return {Exception(check(['TOPDECK']), topdeckGainedCard): bL}


# Cards['REPLACE'].action = replace_action

# Cards['SWINDLER'].action = banditlike


# def torturer_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         gainExc = checkMove(['GAIN'], 'SUPPLY', 'HANDS', ['Curse'])
#         onGainExc = Exception(check(['GAIN'], ['Curse']),
#                               onGains('HANDS'))
#         return {exc: bL for exc in [gainExc, onGainExc]}


# Cards['TORTURER'].action = torturer_action


# def tradepost_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         onGainExc = Exception(check(['GAIN'], ['Silver']),
#                               onGains('HANDS'))
#         gainExc = checkMove(['GAIN'], 'SUPPLY', 'HANDS', ['Silver'])
#         return {exc: bL for exc in [onGainExc, gainExc]}


# Cards['TRADING POST'].action = tradepost_action


# def ambassador_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         return {checkMove(['RETURN TO'], 'HANDS', 'SUPPLY'): bL}


# Cards['AMBASSADOR'].action = ambassador_action

# Cards['EMBARGO'].action = selftrasher


# def explorer_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         onGainExc = Exception(check(['GAIN'], ['Silver', 'Gold']),
#                               onGains('HANDS'))
#         gainExc = checkMove(['GAIN'], 'SUPPLY', 'HANDS', ['Silver', 'Gold'])
#         return {exc: bL for exc in [onGainExc, gainExc]}


# Cards['EXPLORER'].action = explorer_action


# def island_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         islandStack = Cardstack({"ISLAND": 1})
#         otherStuff = move.items - islandStack

#         def islandSetaside(islandStack, otherStuff):
#             def out_function(move, i, bL, moves, cS):
#                 cS.transfer(move.player, 'INPLAYS', 'OTHERS', islandStack)
#                 cS.transfer(move.player, 'HANDS', 'OTHERS', otherStuff)
#             return out_function

#         return {Exception(check(['PUT ONTO']),
#                           islandSetaside(islandStack, otherStuff)): bL}


# Cards['ISLAND'].action = island_action

# Cards['LOOKOUT'].action = sentrylike


# def nv_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         pullExc = checkMove(['PUT INHAND'], 'OTHERS', 'HANDS')
#         setExc = checkMove(['SET ASIDE WITH'], 'DECKS', 'OTHERS')
#         return {exc: bL for exc in [pullExc, setExc]}


# Cards['NATIVE VILLAGE'].action = nv_action

# Cards['NAVIGATOR'].action = decksifter


# def pearldiver_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         return {checkMove(['TOPDECK'], 'DECKS', 'DECKS'): bL}


# Cards['PEARL DIVER'].action = pearldiver_action

# Cards['PIRATE SHIP'].action = banditlike


# def seahag_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         gainExc = checkMove(['GAIN'], 'SUPPLY', 'DECKS', ['CURSE'])
#         onGainExc = Exception(check(['GAIN'], ['CURSE']),
#                               onGains('DECKS'))
#         return {exc: bL for exc in [exc_revealDiscard, gainExc, onGainExc]}


# Cards['SEA HAG'].action = seahag_action


# def tmap_action(move, i, bL, moves, cS):
#     def tmap_one(cM):
#         if str(move.pred) == 'TRASH':
#             if move.items['TREASURE MAP'] == 1:
#                 return True
#         return False

#     def tmap_two(cM):
#         if str(move.pred) == 'TRASH':
#             if move.items['TREASURE MAP'] == 2:
#                 return True
#         return False

#     def tmap_double_trash(move, i, bL, moves, cS):
#         single_map = Cardstack({'TREASURE MAP': 1})
#         cS.transfer(move.player, 'INPLAYS', 'TRASH', single_map)
#         cS.transfer(move.player, 'HANDS', 'TRASH', single_map)

#     if str(move.pred) in PLAY_PREDS:
#         return {Exception(tmap_one, moveFunct('INPLAYS', 'TRASH')): bL,
#                 Exception(tmap_two, tmap_double_trash): bL}


# Cards['TREASURE MAP'].action = tmap_action


# def apoth_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         return {exc_revealTopdeck: bL}


# Cards['APOTHECARY'].action = apoth_action

# Cards['GOLEM'].action = golemlike


# def herbalist_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         return {checkMove(['TOPDECK'], 'INPLAYS', 'DECKS'): bL}


# Cards['HERBALIST'].action = herbalist_action

# Cards['SCRYING POOL'].action = decksifter


# def vineyard_worth(gS, player):
#     playerDeck = gS.crunch(PERSONAL_ZONES, (player))
#     return sum([playerDeck[item] for item in playerDeck if
#                 item in actionList]) // 3


# Cards['VINEYARD'].worth = vineyard_worth


# def countinghouse_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         return {checkMove(['PUT INHAND'], 'DISCARDS', 'HANDS'): bL}


# Cards['COUNTING HOUSE'].action = countinghouse_action

# Cards['LOAN'].action = banditlike


# def mint_action(move, i, bL, moves, cS):
#     if str(move.pred) in ['BUY AND GAIN', 'BUY']:
#         return {checkMove(['TRASH'], 'INPLAYS', 'TRASH'): bL}


# Cards['MINT'].action = mint_action

# Cards['RABBLE'].action = decksifter

# Cards['VENTURE'].action = golemlike


# def bagofgold_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         gainExc = checkMove(['GAIN'], 'SUPPLY', 'DECKS', ['GOLD'])
#         onGainExc = Exception(check(['GAIN'], ['GOLD']),
#                               onGains('DECKS'))
#         return {exc: bL for exc in [gainExc, onGainExc]}


# Cards['BAG OF GOLD'].action = bagofgold_action


# def fairgrounds_worth(gS, player):
#     playerDeck = gS.crunch(PERSONAL_ZONES, (player))
#     return len(playerDeck.cardList()) // 5


# Cards['FAIRGROUNDS'].worth = fairgrounds_worth


# def farmvillage_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         return {exc_revealDiscard: bL}


# Cards['FARMING VILLAGE'].action = deckchuck

# Cards['FORTUNE TELLER'].action = decksifter

# Cards['HARVEST'].action = deckchuck


# def horseTraders_action(move, i, bL, moves, cS):
#     if str(move.pred) == 'REACT':
#         return {checkMove(['SET ASIDE'], 'HANDS', 'OTHERS',
#                           ['HORSE TRADERS']): 2}


# Cards['HORSE TRADERS'].action = horseTraders_action


# def hop_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         return {checkMove(['TRASH'], 'INPLAYS', 'TRASH',
#                           ['HORN OF PLENTY']): bL}


# Cards['HORN OF PLENTY'].action = hop_action

# Cards['HUNTING PARTY'].action = deckchuck

# Cards['JESTER'].action = deckchuck

# Cards['TOURNAMENT'].action = deckGain


# def steed_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         onGainExc = Exception(check(['GAIN']), onGains('DECKS'))
#         gainExc = checkMove(['GAIN'], 'SUPPLY', 'DECKS', ['Silver'])
#         return {exc: bL for exc in [onGainExc, gainExc]}


# Cards['TRUSTY STEED'].action = steed_action

# Cards['CARTOGRAPHER'].action = decksifter

# Cards['DEVELOP'].action = deckGain

# Cards['DUCHESS'].action = decksifter


# def fg_action(move, i, bL, moves, cS):
#     if str(move.pred) in ['TRASH']:
#         gainExc = checkMove(['GAIN'], 'SUPPLY', 'DECKS', ['GOLD'])
#         onGainExc = Exception(check(['GAIN'], ['GOLD']),
#                               onGains('DECKS'))
#         return {exc: bL for exc in [gainExc, onGainExc]}


# Cards["FOOL'S GOLD"].action = fg_action


# def igg_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         gainExc = checkMove(['GAIN'], 'SUPPLY', 'HANDS', ['COPPER'])
#         onGainExc = Exception(check(['GAIN'], ['COPPER']),
#                               onGains('HANDS'))
#         return {exc: bL for exc in [gainExc, onGainExc]}


# Cards['ILL-GOTTEN GAINS'].action = igg_action

# Cards['JACK OF ALL TRADES'].action = decksifter


# def mandarin_action(move, i, bL, moves, cS):
#     if str(move.pred) in GAIN_PREDS:
#         return {checkMove(['TOPDECK'], 'INPLAYS', 'DECKS'): bL}


# Cards['MANDARIN'].action = mandarin_action


# def brigand_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS or str(move.pred) == 'BUY':
#         return {exc: bL for exc in [exc_revealTrash,
#                                     exc_standardTrash,
#                                     exc_revealDiscard]}


# Cards['NOBLE BRIGAND'].action = brigand_action

# Cards['ORACLE'].action = decksifter


# def silkroad_worth(gameState, player):
#     playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
#     return sum([playerDeck[item] for item in playerDeck if
#                 str(item) in victoryCards]) // 4


# Cards['SILK ROAD'].worth = silkroad_worth

# Cards['ARMORY'].action = deckGain

# Cards['BAND OF MISFITS'].action = emulate


# def beggar_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         gainExc = checkMove(['GAIN'], 'SUPPLY', 'HANDS', ['COPPER'])
#         onGainExc = Exception(check(['GAIN'], ['COPPER']),
#                               onGains('HANDS'))
#         return {exc: bL for exc in [gainExc, onGainExc]}


# Cards['BEGGAR'].action = beggar_action

# Cards['CATACOMBS'].action = deckchuck

# Cards['COUNTERFEIT'].action = selftrasher


# def knightSuicide(knightPlayer):
#     def out_function(move):
#         isKnight = move.items.primary() in KNIGHTS
#         return str(move.pred) == 'TRASH' and move.player == knightPlayer and \
#             isKnight
#     return out_function


# def knightTrash(knightPlayer):
#     def out_function(move):
#         isKnight = move.items.primary() in KNIGHTS
#         return str(move.pred) == 'TRASH' and move.player != knightPlayer and \
#             isKnight
#     return out_function


# def knightAction(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         exc.append(exc_revealDiscard)
#         trashExc = Exception(knightsTrash(move.player),
#                              moveFunct('DECKS', 'TRASH'))
#         onTrashExc = Exception(knightsTrash(move.player),
#                                standardOnTrash)
#         suicideExc = Exception(knightsSuicide(move.player),
#                                moveFunct('INPLAYS', 'TRASH'))
#         return {exc: bL for exc in [exc_revealDiscard,
#                                     trashExc,
#                                     onTrashExc,
#                                     suicideExc]}


# def annaAction(move, i, bL, moves, cS):
#     def annaTrash(knightPlayer):
#         def out_function(move):
#             trashPart = str(move.pred) == 'TRASH' and \
#                 move.items.primary() != 'DAME ANNA'
#             return trashPart and move.player == knightPlayer
#         return out_function

#     if str(move.pred) in PLAY_PREDS:
#         exc.append(exc_revealDiscard)
#         trashExc = Exception(knightsTrash(move.player),
#                              moveFunct('DECKS', 'TRASH'))
#         onTrashExc = Exception(knightsTrash(move.player),
#                                standardOnTrash)
#         suicideExc = Exception(knightsSuicide(move.player),
#                                moveFunct('INPLAYS', 'TRASH'))
#         annaTrash = Exception(annaTrash(move.player),
#                               moveFunct('HANDS', 'TRASH'))
#         annaOnTrash = Exception(annaTrash(move.player),
#                                 standardOnTrash)
#         return {exc: bL for exc in [exc_revealDiscard,
#                                     trashExc,
#                                     onTrashExc,
#                                     suicideExc,
#                                     annaTrash,
#                                     annaOnTrash]}


# def michaelAction(move, i, bL, moves, cS):
#     def onReveal(l):
#         def out_function(move, i, bL, moves, cS):
#             return {exc_revealDiscard: l - 1}
#         return out_function

#     if str(move.pred) in PLAY_PREDS:
#         michaelReveal = Exception(check(['REVEAL']), onReveal(bL))
#         trashExc = Exception(knightsTrash(move.player),
#                              moveFunct('DECKS', 'TRASH'))
#         onTrashExc = Exception(knightsTrash(move.player),
#                                standardOnTrash)
#         suicideExc = Exception(knightsSuicide(move.player),
#                                moveFunct('INPLAYS', 'TRASH'))
#         return {exc: bL for exc in [michaelReveal,
#                                     trashExc,
#                                     onTrashExc,
#                                     suicideExc]}


# for knight in KNIGHTS:
#     if knight == 'DAME ANNA':
#         Cards[knight].action = annaAction
#     elif knight == 'SIR MICHAEL':
#         Cards[knight].action = michaelAction
#     else:
#         Cards[knight].action = knightAction


# def deathcart_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         trashExc = checkMove(['TRASH'], 'INPLAYS', 'TRASH', ['DEATH CART'])
#         onTrashExc = Exception(check(['TRASH'], ['DEATH CART']),
#                                standardOnTrash)
#         return {exc: bL for exc in [trashExc, onTrashExc]}


# Cards['DEATH CART'].action = deathcart_action


# def feodum_worth(gameState, player):
#     playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
#     return playerDeck['SILVER'] // 3


# Cards['FEODUM'].worth = feodum_worth


# def fortress_action(move, i, bL, moves, cS):
#     if str(move.pred) == 'TRASH':
#         return {checkMove(['PUT INHAND'], 'TRASH', 'HANDS'): bL}


# Cards['FORTRESS'].action = fortress_action


# def graverobber_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         for scan in moves[i + 1: i + bL]:
#             if str(scan.pred) == 'TRASH':
#                 return {}
#         else:
#             gainExc = checkMove(['GAIN'], 'TRASH', 'DECKS')
#             onGainExc = Exception(check(['GAIN']),
#                                   onGains('DECKS'))
#             return {exc: bL for exc in [gainExc, onGainExc]}


# Cards['GRAVEROBBER'].action = graverobber_action


# def hermit_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         playerDiscard = cS[('DISCARDS', move.player)]

#         def discardTrash(playerDiscard):
#             def out_function(move):
#                 return playerDiscard > move.items and str(move.pred) == 'TRASH'
#             return out_function

#         return {Exception(discardTrash(playerDiscard),
#                           moveException('DISCARDS', 'TRASH')): bL}


# Cards['HERMIT'].action = hermit_action

# Cards['IRONMONGER'].action = decksifter

# Cards['PILLAGE'].action = selftrasher

# Cards['PROCESSION'].action = selftrasher

# Cards['REBUILD'].action = banditlike


# def rogue_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         rogueGain = checkMove(['GAIN'], 'TRASH', 'DISCARDS')
#         rogueOnGain = Exception(check(['GAIN']),
#                                 standardOnGains('DISCARDS', move.items))
#         return {exc: bL for exc in [exc_revealTrash,
#                                     exc_standardTrash,
#                                     exc_revealDiscard,
#                                     rogueGain,
#                                     rogueOnGain]}


# Cards['ROGUE'].action = rogue_action

# Cards['SAGE'].action = deckchuck

# Cards['SCAVENGER'].action = harbingerlike

# Cards['SURVIVORS'].action = decksifter

# Cards['VAGRANT'].action = deckchuck

# Cards['WANDERING MINSTREL'].action = decksifter

# Cards['ADVISOR'].action = deckchuck

# Cards['DOCTOR'].action = sentrylike


# # 234: Herald
# def herald_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         playExc = checkMove(['PLAY'], 'DECKS', 'INPLAYS')
#         onPlayExc = Exception(check(['PLAY']), standardOnPlay)
#         return {exc: bL for exc in [playExc, onPlayExc]}

#     if str(move.pred) == 'BUY':
#         return {exc_harbinger: bL}


# Cards['HERALD'].action = herald_action

# Cards['JOURNEYMAN'].action = deckchuck

# Cards['TAXMAN'].action = deckGain

# Cards['ARTIFICER'].action = deckGain


# # 246: Bonfire
# def bonfire_action(move, i, bL, moves, cS):
#     if str(move.pred) == 'BUY':
#         return {exc: bL for exc in [exc_inplayTrash, exc_standardTrash]}


# Cards['BONFIRE'].action = bonfire_action

# Cards['COIN OF THE REALM'].action = standardReserve


# def distantlands_worth(gS, player):
#     playerDeck = gS.crunch(['DECKS', 'OTHERS'], (player))
#     total = playerDeck['DISTANT LANDS']

#     return gS[('OTHERS', player)]['DISTANT LANDS'] / total


# Cards['DISTANT LANDS'].worth = distantlands_worth

# Cards['DUPLICATE'].action = standardReserve

# Cards['GIANT'].action = banditlike

# Cards['GUIDE'].action = standardReserve

# Cards['MAGPIE'].action = decksifter

# Cards['RATCATCHER'].action = standardReserve


# def razeAction(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         razeExc = checkMove(['TRASH'], 'INPLAYS', 'TRASH', ['Raze'])
#         return {exc: bL for exc in [razeExc, exc_revealDiscard]}


# Cards['RAZE'].action = razeAction

# Cards['ROYAL CARRIAGE'].action = standardReserve


# def save_action(move, i, bL, moves, cS):
#     if str(move.pred) == 'BUY':
#         return {checkMove(['PUT INHAND'], 'OTHERS', 'HANDS'):
#                 findRemainingSteps(i, moves)}


# Cards['SAVE'].action = save_action


# def scoutingparty_action(move, i, bL, moves, cS):
#     if str(move.pred) == 'BUY':
#         return {exc: bL for exc in [exc_revealTopdeck, exc_revealDiscard]}


# Cards['SCOUTING PARTY'].action = save_action

# Cards['TEACHER'].action = standardReserve


# def transmogrify_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         return {checkMove(['PUT ONTO'], 'INPLAYS', 'OTHERS'): bL}

#     if str(move.pred) == 'CALL':
#         gainExc = checkMove(['GAIN'], 'SUPPLY', 'HANDS')
#         onGainExc = Exception(check(['GAIN']), onGains('HANDS'))
#         for l in range(2, len(moves) - i):
#             if moves[i + l].indent == 0:
#                 break
#         return {exc: l for exc in [gainExc, onGainExc]}


# Cards['TRANSMOGRIFY'].action = transmogrify_action


# def warrior_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         return {exc: bL for exc in [checkMove(['TRASH'], 'DISCARDS', 'TRASH'),
#                                     exc_standardTrash,
#                                     exc_revealDiscard]}


# Cards['WARRIOR'].action = transmogrify_action

# Cards['WINE MERCHANT'].action = transmogrify_action

# Cards['PATRICIAN'].action = decksifter

# Cards['SETTLERS'].action = discardToHand

# Cards['BUSTLING VILLAGE'].action = discardToHand


# def rocks_action(move, i, bL, moves, cS):
#     if str(move.pred) in GAIN_PREDS:
#         if cS['PHASE'] == 1:
#             gainExc = checkMove(['GAIN'], 'SUPPLY', 'DECKS')
#             onGainExc = Exception(check(['GAIN']),
#                                   onGains('DECKS'))
#             return {exc: bL for exc in [gainExc, onGainExc]}
#         else:
#             gainExc = checkMove(['GAIN'], 'SUPPLY', 'HANDS')
#             onGainExc = Exception(check(['GAIN']),
#                                   onGains('HANDS'))
#             return {exc: bL for exc in [gainExc, onGainExc]}


# Cards['ROCKS'].action = rocks_action


# def gladiator_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         return {checkMove(['TRASH'], 'SUPPLY', 'TRASH', ['GLADIATOR']): bL}


# Cards['GLADIATOR'].action = gladiator_action

# CASTLES = ['HUMBLE CASTLE', 'CRUMBLING CASTLE', 'SMALL CASTLE',
#            'HAUNTED CASTLE', 'OPULENT CASTLE', 'SPRAWLING CASTLE',
#            'GRAND CASTLE', 'KING\'S CASTLE']


# def humbleCastle_worth(gS, player):
#     playerDeck = gS.crunch(PERSONAL_ZONES, (player))
#     return sum([playerDeck[item] for item in playerDeck if
#                 item in castles])


# def kingsCastle_worth(gS, player):
#     playerDeck = gS.crunch(PERSONAL_ZONES, (player))
#     return 2 * sum([playerDeck[item] for item in playerDeck if
#                     item in castles])


# Cards['HUMBLE CASTLE'].worth = humbleCastle_worth


# def smallcastle_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         return {checkMove(['TRASH'], 'INPLAYS', 'TRASH', ['SMALL CASTLE']): bL}


# Cards['SMALL CASTLE'].worth = humbleCastle_worth

# Cards["KING'S CASTLE"].worth = kingsCastle_worth


# def archive_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         return {checkMove(['SET ASIDE'], 'DECKS', 'OTHERS'): bL}


# Cards['ARCHIVE'].action = archive_action


# def banditfort_worth(gameState, player):
#     playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
#     return sum([-2 * playerDeck[item] for item in playerDeck if
#                 item in ['SILVER', 'GOLD']])


# Cards['BANDIT FORT'].worth = banditfort_worth

# Cards['CHARIOT RACE'].action = decksifter


# def engineer_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         def engineerTrashCondition(move):
#             return move.indent == 0 and \
#                 str(move.pred) == 'TRASH' and \
#                 move.items.primary() == 'ENGINEER'

#         trashExc = checkMove(['TRASH'], 'INPLAYS', 'TRASH', ['ENGINEER'])
#         if move.indent == 0:
#             delayedTrash = Exception(engineerTrashCondition,
#                                      moveFunct('INPLAYS', 'TRASH'))
#             return {trashExc: bL, delayedTrash: bL + 2}
#         else:
#             return {trashExc: bL}


# Cards['ENGINEER'].action = engineer_action


# def farmmarket_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         return {checkMove(['TRASH'], 'INPLAYS', 'TRASH', ["FARMERS' MARKET"])}


# Cards["FARMERS' MARKET"].action = farmmarket_action


# def fountain_worth(gameState, player):
#     playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
#     if playerDeck['COPPER'] >= 10:
#         return 15
#     return 0


# Cards['FOUNTAIN'].worth = fountain_worth


# def keep_worth(gameState, player):
#     playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
#     otherDeck = gameState.crunch(PERSONAL_ZONES, [1 - player])
#     total = 0

#     for card in playerDeck:
#         if card in treasures:
#             if playerDeck[card] >= otherDeck[card]:
#                 total += 5

#     return total


# Cards['KEEP'].worth = keep_worth


# def museum_worth(gameState, player):
#     playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
#     return 2 * len(playerDeck.cardList())


# Cards['MUSEUM'].worth = museum_worth


# def obelisk_worth(gameState, player):
#     playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
#     return sum(playerDeck[c] for c in gameState['OBELISK'])


# Cards['OBELISK'].worth = obelisk_worth


# # 352: Orchard
# def orchard_worth(gameState, player):
#     playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
#     total = 0

#     for card in playerDeck:
#         if card in actionList:
#             if playerDeck[card] >= 3:
#                 total += 4

#     return total


# Cards['ORCHARD'].worth = orchard_worth

# Cards['OVERLORD'].action = emulate


# def palace_worth(gameState, player):
#     playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
#     treasures = ['COPPER', 'SILVER', 'GOLD']
#     counts = [0, 0, 0]

#     for card in treasures:
#         counts[treasures.index(card)] = playerDeck[card]

#     return 3 * min(counts)


# Cards['PALACE'].worth = palace_worth


# def salt_action(move, i, bL, moves, cS):
#     if str(move.pred) == 'BUY':
#         return{checkMove(['TRASH'], 'SUPPLY', 'TRASH'): bL}


# Cards['SALT THE EARTH'].action = salt_action


# def tower_worth(gameState, player):
#     playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
#     total = 0

#     for card in playerDeck:
#         if standardCards[card].supply_type == 0 and\
#                 card not in gameState[('SUPPLY', 0)]:
#             if card not in victoryCards:
#                 total += playerDeck[card]

#     return total


# Cards['TOWER'].worth = tower_worth


# def arch_worth(gameState, player):
#     playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
#     counts = sorted([playerDeck[card] for card in playerDeck if
#                      card in actionList], reverse=True)
#     counts = counts + [0, 0]

#     return 3 * counts[1]


# Cards['TRIUMPHAL ARCH'].worth = arch_worth


# def wall_worth(gameState, player):
#     playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
#     return 15 - max(15, len(playerDeck))


# Cards['WALL'].worth = wall_worth


# def den_worth(gameState, player):
#     playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
#     return -3 * len([card for card in playerDeck if playerDeck[card] == 1])


# Cards['WOLF DEN'].worth = den_worth


# def miserable_action(move, i, bL, moves, cS):
#     if str(move.pred) == ['TAKES']:
#         cS.vps[move.player] -= 2


# Cards['MISERABLE'].action = miserable_action

# Cards['TWICE MISERABLE'].action = miserable_action

# Cards['CHANGELING'].action = selftrasher


# def druid_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         t = {Exception(check('RECEIVE BOONHEX'), empty): bL}
#         for scan in moves[i + 1: i + bL]:
#             if str(scan.pred) == 'RECEIVE BOONHEX':
#                 whichBoon = scan.items.primary()
#                 break

#         if whichBoon == "THE SUN'S GIFT":
#             t[exc_revealTopdeck] = bL
#             t[exc_revealDiscard] = bL

#         elif whichBoon == "THE MOON'S GIFT":
#             t[exc_harbinger] = bL

#         return t


# Cards['DRUID'].action = druid_action


# def hound_action(move, i, bL, moves, cS):
#     if str(move.pred) in ['REACT']:
#         return {checkMove(['SET ASIDE'], 'DISCARDS', 'OTHERS',
#                           ['FAITHFUL HOUND']): 2}


# Cards['FAITHFUL HOUND'].action = hound_action


# def monastery_action(move, i, bL, moves, cS):
#     # Possible conflicts: Exorcist - hence, trash inplay first.
#     if str(move.pred) in PLAY_PREDS:
#         def monastery_trash(move, i, bL, moves, cS):
#             moveCoppers = move.items['COPPER']
#             inPlayCoppers = cS[('INPLAYS', move.player)]['COPPER']
#             coppersToKill = min(moveCoppers, inPlayCoppers)

#             if coppersToKill > 0:
#                 copperStack = Cardstack({'COPPER': coppersToKill})
#                 itemsSansCoppers = move.items - copperStack

#                 cS.move(move.player, 'HANDS', 'TRASH', itemsSansCoppers)
#                 cS.move(move.player, 'INPLAYS', 'TRASH', copperStack)
#             else:
#                 transfer('HANDS', 'TRASH', move, cS)

#         return {exc: bL for exc in [Exception(check(['TRASH'], ['COPPER']),
#                                               monastery_trash),
#                                     exc_standardTrash]}


# Cards['MONASTERY'].action = monastery_action


# def necromancer_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         playExc = checkMove(['PLAY'], 'TRASH', 'TRASH')
#         onPlayExc = Exception(check(['PLAY']), standardOnPlay)
#         return {exc: bL for exc in [playExc, onPlayExc]}


# Cards['NECROMANCER'].action = necromancer_action

# Cards['NIGHT WATCHMAN'].action = decksifter


# def pixie_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         for scan in moves[i + 1: i + bL]:
#             if str(scan.pred) == 'TAKES BOONHEX':
#                 whichBoon = scan.items.primary()
#                 break

#         if whichBoon == 'The Flame\'s Gift':
#             pixieStack = Cardstack({"PIXIE": 1})
#             otherThings = move.items - pixieStack

#             def pixieTrash(pixieStack, otherThings):
#                 def out_function(move, i, bL, moves, cS):
#                     cS.move(move.player, 'INPLAYS', 'TRASH', pixieStack)
#                     cS.move(move.player, 'HANDS', 'TRASH', otherThings)
#                 return out_function

#             pixieTrashExc = Exception(check(['TRASH'], ['Pixie']),
#                                       pixieTrash(pixieStack, otherThings))
#             pixieOnTrashExc = Exception(check(['TRASH'], ['Pixie']),
#                                         standardOnTrash)
#             return {exc: bL for exc in [pixieTrashExc, pixieOnTrashExc]}
#         else:
#             t = {checkMove(['TRASH'], 'INPLAYS', 'TRASH'): bL}

#             if whichBoon == 'The Sun\'s Gift':
#                 t[exc_revealTopdeck] = bL
#                 t[exc_revealDiscard] = bL

#             elif whichBoon == 'The Moon\'s Gift':
#                 t[exc_harbinger] = bL
#             return t


# Cards['PIXIE'].action = pixie_action

# Cards['TRAGIC HERO'].action = selftrasher


# def vampire_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         t = {checkMove(['RETURN'], 'INPLAYS', 'SUPPLY', ['VAMPIRE']): bL}
#         t.append(standard_boonhex(cM, gS, exc, tExc, pers))
#         return t


# Cards['VAMPIRE'].action = vampire_action

# Cards['MAGIC LAMP'].action = selftrasher


# def pasture_worth(gameState, player):
#     playerDeck = gameState.crunch(PERSONAL_ZONES, (player))
#     return playerDeck['ESTATE']


# Cards['PASTURE'].worth = pasture_worth


# def bats_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         return {checkMove(['RETURN'], 'INPLAYS', 'SUPPLY', ['BAT']): bL}


# Cards['BAT'].action = bats_action


# def ghost_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         setExc = checkMove(['SET ASIDE'], 'DECKS', 'OTHERS')
#         return {exc: bL for exc in [exc_revealDiscard, setExc]}


# Cards['GHOST'].action = ghost_action

# Cards["WILL-O'-WISP"].action = decksifter


# def wish_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         gainExc = checkMove(['GAIN'], 'SUPPLY', 'HANDS')
#         onGainExc = Exception(check(['GAIN']), onGains('HANDS'))
#         return {exc: bL for exc in [gainExc, onGainExc]}


# Cards['WISH'].action = wish_action


# def zombiemason_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         trashExc = checkMove(['TRASH'], 'DECKS', 'TRASH')
#         return {exc: bL for exc in [trashExc, exc_standardTrash]}


# Cards['ZOMBIE MASON'].action = zombiemason_action

# Cards['ZOMBIE SPY'].action = decksifter

# Cards['ENVOY'].action = deckchuck


# def prince_action(move, i, bL, moves, cS):
#     if str(move.pred) in PLAY_PREDS:
#         return{checkMove(['SET ASIDE'], 'HANDS', 'OTHERS'): bL}


# Cards['PRINCE'].action = prince_action


# def summon_action(move, i, bL, moves, cS):
#     if str(move.pred) == 'BUY':
#         return{checkMove(['SET ASIDE'], 'SUPPLY', 'OTHERS'): bL}


# Cards['SUMMON'].action = summon_action