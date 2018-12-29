from .Cardstack import *
from .Exception import *
from copy import deepcopy


playPreds = ('PLAY', 'PLAY COIN', 'THRONE', 'THRONE GENERIC',
             'THRONE COIN', 'KING')

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


def set_phase(action):
    def out_function(moves, i, blockLength, state):
        if moves[i].indent == 0:
            state.phase = 1
        action(moves, i, blockLength, state)
    return out_function


def moveFunct(src, dest):
    def out_function(moves, i, blockLength, state):
        state.move(moves[i].player, src, dest, moves[i].items[0])
    return out_function


def checkMove(predList, src, dest, targetList=[]):
    return Exception(check(predList, targetList),
                     moveFunct(src, dest))


def move_play(source, dest='INPLAYS'):
    def out_function(moves, i, blockLength, state):
        state.move(moves[i].player, source, dest, moves[i].items[0])
        standard_plays(moves, i, blockLength, state)
    return out_function


exc_revealTopdeck = checkMove(['TOPDECK'], 'DECKS', 'DECKS')
exc_revealDiscard = checkMove(['DISCARD'], 'DECKS', 'DISCARDS')
exc_harbinger = checkMove(['TOPDECK'], 'DISCARDS', 'DECKS')
exc_settlers = checkMove(['PUT INHAND'], 'DISCARDS', 'HANDS')
exc_gainHand = checkMove(['GAIN'], 'SUPPLY', 'HANDS')


def standard_trash(source):
    def out_function(moves, i, blockLength, state):
        move = moves[i]
        target = move.items[0].primary
        if target == 'ESTATE':
            target = state.inherited[move.player]
        if i + blockLength < len(moves) and\
                moves[i + blockLength].pred == 'GAIN' and\
                moves[i + blockLength].items[0].primary in \
                ['MADMAN', 'MERCENARY']:
            state.move(move.player, 'INPLAYS', 'TRASH', move.items[0])
        else:
            state.move(move.player, source, 'TRASH', move.items[0])

        triggers = {'FORTRESS': [checkMove(['PUT INHAND'], 'TRASH', 'HANDS')]
                    }

        if target in triggers:
            for exc in triggers[target]:
                newExc = deepcopy(exc)
                newExc.lifespan = blockLength
                newExc.indents = [moves[i].indent + 1]
                state.exceptions.add(newExc)

        if target == 'ROCKS':
            if state.phase == 2:
                newExc = gainTo('SUPPLY', 'DECKS')
            else:
                newExc = gainTo('SUPPLY', 'HANDS')
            newExc.lifespan = blockLength
            newExc.indents = [moves[i].indent + 1]
            state.exceptions.add(newExc)

    return out_function


exc_revealTrash = Exception(check(['TRASH']), standard_trash('DECKS'))
exc_supplyTrash = Exception(check(['TRASH']), standard_trash('SUPPLY'))
exc_inplayTrash = Exception(check(['TRASH']), standard_trash('INPLAYS'))


def gainTo(source, destination):
    return Exception(check(['GAIN']), standard_gains(source, destination))

# -- PREDS -- #


def new_turn_action(moves, i, blockLength, state):
    state.activePlayer = moves[i].player
    state.phase = 0
    state.coins = 0
    state.actions = 1
    state.buys = 1

    newDurations = []
    for stack, life in state.durations[moves[i].player]:
        if life != 0:
            if life > 0:
                life -= 1
            newDurations.append((stack, life))
    state.durations[moves[i].player] = newDurations
    state.linkedPlays = []
    state.amuletSilvers = 0
    state.cargoShips = 0
    state.bridges = 0


Preds['NEW TURN'].action = new_turn_action


def turn_start_action(moves, i, blockLength, state):
    def start_gain(moves, i, blockLength, state):
        move = moves[i]
        for item in move.items[0]:
            if item != 'SILVER':
                state.move(move.player, 'SUPPLY', 'HANDS', move.items[0])
                return

        if move.items[0]['SILVER'] <= state.amuletSilvers:
            state.move(move.player, 'SUPPLY', 'DISCARDS', move.items[0])
            state.amuletSilvers -= move.items[0]['SILVER']
        else:
            state.move(move.player, 'SUPPLY', 'HANDS', move.items[0])

    def start_piazza(moves, i, blockLength, state):
        state.exceptions.add(Exception(check(['TOPDECK']),
                                       empty,
                                       lifespan=2,
                                       indents=[moves[i].indent]))
        state.exceptions.add(Exception(check(['PLAY']),
                                       move_play('DECKS'),
                                       lifespan=2,
                                       indents=[moves[i].indent]))

    state.phase = 0
    exceptions = [checkMove(['PUT INHAND'], 'OTHERS', 'HANDS'),
                  Exception(check(['GAIN']), start_gain),
                  Exception(check(['PLAY']), move_play('OTHERS')),
                  Exception(check(['REVEAL']), start_piazza)]
    for exc in exceptions:
        newExc = deepcopy(exc)
        newExc.lifespan = blockLength
        newExc.indent = [moves[i].indent + 1]
        state.exceptions.add(newExc)

    # Cobbler / Amulet stuff
    amuletPlays = 0
    for stack, life in state.durations[moves[i].player]:
        amuletPlays += stack['AMULET']

    index = i + 1
    while index < i + blockLength:
        secondary = moves[index]
        if secondary.pred == 'COINS GENERIC' and \
                secondary.items[0].primary == 'AMULET':
            amuletPlays -= 1
        elif secondary.pred == 'TRASH' and \
                secondary.indent == moves[i].indent + 1:
            amuletPlays -= 1
        elif secondary.pred == 'CALL':
            index += 1
        index += 1

    state.amuletSilvers = amuletPlays


Preds['TURN START'].action = turn_start_action


def end_buys_action(moves, i, blockLength, state):
    exceptions = [checkMove(['DISCARD'], 'TAVERN', 'DISCARDS',
                            ['WINE MERCHANT'])]
    for exc in exceptions:
        newExc = deepcopy(exc)
        newExc.lifespan = blockLength
        newExc.indent = [moves[i].indent + 1]
        state.exceptions.add(newExc)


Preds['END BUYPHASE'].action = end_buys_action


def donate_action(moves, i, blockLength, state):
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


Preds['BETWEEN TURNS'].action = donate_action

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
        target = deepcopy(move.items[0])
        if target == 'ESTATE':
            target = state.inherited[move.player]
        if move.indent == 0:
            state.phase = 2

        def move_target(endpoint):
            def out_function(moves, i, blockLength, state):
                source = get_gain_dest(target.primary) if \
                    destination == 'DISCARDS' else destination
                block = Cardstack({target.primary: 1})
                state.move(moves[i].player, source, endpoint, block)
            return out_function

        def cargo_check(move):
            return move.pred == 'SET ASIDE WITH' and \
                len(move.items) > 1 and \
                move.items[1].primary == 'CARGO SHIP'

        def cargo_move(moves, i, blockLength, state):
            state.move(moves[i].player, destination, 'OTHERS',
                       moves[i].items[0])
            twinned = sum([stack['CARGO SHIP'] for plays, stack, dur in
                           state.durations])
            soloShips = state.cargoShips - twinned
            block = [Cardstack({'CARGO SHIP': 1}), 1]
            if state.cargoCount < soloShips:
                state.durations[moves[i].player].append(block)
            else:
                twinCapacity = sum([len(plays) for plays, stack, dur in
                                    state.durations if dur])
                if twinCapacity + soloShips == state.cargoCount:
                    for j in range(len(state.linkedPlays)):
                        plays, cards, ship = state.linkedPlays[j]
                        if 'CARGO SHIP' in cards and not ship:
                            newDur = [cards, 1]
                            state.linkedPlays[j][2] = newDur

            state.cargoCount += 1

        def innovation_action(moves, i, blockLength, state):
            target = moves[i].items[0].primary
            endpoint = get_gain_dest(target) if \
                destination == 'DISCARDS' else destination
            state.move(moves[i].player, endpoint, 'OTHERS', moves[i].items[0])
            state.exceptions.add(Exception(check(['PLAY']),
                                           move_play('OTHERS'),
                                           lifespan=2,
                                           indents=[moves[i].indent]))

        # If default, check for exceptional gain destinations
        if destination == 'DISCARDS':
            for card in target:
                block = Cardstack({card: target[card]})
                state.move(move.player, source, get_gain_dest(card), block)
        else:
            state.move(move.player, source, destination, target)

        # Topdeck / trash reactions / Innovation
        for secondary in moves[i + 1: i + blockLength]:
            if check(['REACT'],
                     ['ROYAL SEAL', 'WATCHTOWER', 'TRAVELLING FAIR',
                      'TRACKER'])(secondary) and \
                    secondary.indent == move.indent + 1:
                for action, endpoint in [('TOPDECK', 'DECKS'),
                                         ('TRASH', 'TRASH')]:
                    newExc = Exception(check([action],
                                             ['CARD', target.primary]),
                                       move_target(endpoint))
                    newExc.lifespan = blockLength
                    newExc.indents = [move.indent + 1]
                    state.exceptions.add(newExc)
                break

        # Cargo Ship
        state.exceptions.add(Exception(cargo_check,
                                       cargo_move,
                                       lifespan=blockLength,
                                       indents=[move.indent + 1]))
        state.exceptions.add(Exception(check(['SET ASIDE']),
                                       innovation_action,
                                       lifespan=blockLength,
                                       indents=[move.indent + 1]))

        def fg_react(moves, i, blockLength, state):
            newExc = deepcopy(checkMove(['GAIN'], 'SUPPLY', 'DECKS',
                                        ['GOLD']))
            newExc.lifespan = blockLength + 1
            newExc.indents = [moves[i].indent]
            state.exceptions.add(newExc)

        def villa_phase(moves, i, blockLength, state):
            state.move(moves[i].player, destination, 'HANDS',
                       moves[i].items[0])
            state.phase = 1

        triggers = {'PROVINCE': [Exception(check(['TRASH'], ["FOOL'S GOLD"]),
                                           fg_react)],
                    'INN': [Exception(check(['SHUFFLE']), empty)],
                    'MANDARIN': [checkMove(['TOPDECK'], 'INPLAYS', 'DECKS')],
                    'VILLA': [Exception(check(['PUT INHAND']), villa_phase)]
                    }

        if target.primary in triggers:
            for exc in triggers[target.primary]:
                newExc = deepcopy(exc)
                newExc.lifespan = blockLength
                newExc.indents = [moves[i].indent + 1]
                state.exceptions.add(newExc)

    return out_function


def gain_experiment(moves, i, blockLength, state):
    state.move(moves[i].player, 'SUPPLY', 'DECKS',
               Cardstack({'EXPERIMENT': 1}))


def get_cost(card, player, state):
    reductions = state.bridges
    highwayLike = ['HIGHWAY', 'BRIDGE TROLL', 'PRINCESS']

    for highway in highwayLike:
        reductions += state['INPLAYS'][player][highway]
    reductions += state['INPLAYS'][player]['PRINCESS']

    if 'a' in Cards[card].types:
        reductions += state['INPLAYS'][player]['QUARRY'] * 2

    if 'CANAL' in state.projects[player]:
        reductions += 1

    if card == 'PEDDLER' and state.phase == 2:
        for inplay in state['INPLAYS'][player]:
            if 'a' in Cards[inplay].types:
                reductions += state['INPLAYS'][player][inplay] * 2

    actualCost = deepcopy(Cards[card].cost)
    actualCost[0] = max(0, actualCost[0])
    return actualCost


def buy_action(moves, i, blockLength, state):
    move = moves[i]
    target = move.items[0].primary

    if move.indent == 0:
        state.phase = 2
        state.buys -= 1

    cost = get_cost(target, move.player, state)
    state.coins -= cost[0]
    if len(cost) > 1:
        state.debt[move.player] += cost[1]

    triggers = {'MINT': [exc_inplayTrash],
                'DOCTOR': [exc_revealTrash, exc_revealDiscard,
                           exc_revealTopdeck],
                'HERALD': [exc_harbinger],
                'BONFIRE': [exc_inplayTrash],
                'SCOUTING PARTY': [exc_revealDiscard, exc_revealTopdeck],
                'ANNEX': [Exception(check(['SHUFFLE']), empty)],
                'SALT THE EARTH': [exc_supplyTrash],
                'SUMMON': [checkMove(['SET ASIDE'], 'SUPPLY', 'OTHERS')]
                }

    if target in triggers:
        for exc in triggers[target]:
            newExc = deepcopy(exc)
            newExc.lifespan = blockLength
            newExc.indents = [moves[i].indent + 1]
            state.exceptions.add(newExc)

    if target == 'SAVE':
        for life in range(1, len(moves) - i):
            if moves[i + life - 1].pred == 'NEW TURN':
                break
        state.exceptions.add(Exception(check(['PUT INHAND']),
                                       moveFunct('OTHERS', 'HANDS'),
                                       lifespan=life,
                                       indents=[0]))

    elif 'p' in Cards[target].types:
        state.projects[move.player].add(target)


def buy_and_gain(moves, i, blockLength, state):
    buy_action(moves, i, blockLength, state)
    standard_gains('SUPPLY')(moves, i, blockLength, state)


Preds['BUY'].action = buy_action
Preds['BUY AND GAIN'].action = buy_and_gain
Preds['GAIN TOPDECK'].action = standard_gains('SUPPLY', 'DECKS')
Preds['GAIN TRASH'].action = standard_gains('TRASH')
Preds['GAIN EXPERIMENT'].action = gain_experiment
Preds['GAIN'].action = standard_gains('SUPPLY')
Preds['TRASH'].action = standard_trash('HANDS')


def discard_action(moves, i, blockLength, state):
    move = moves[i]
    state.move(move.player, 'HANDS', 'DISCARDS', move.items[0])


Preds['DISCARD'].action = discard_action


def get_stayout_duration(moves, i, state):
    move = moves[i]
    target = move.items[0].primary
    if target == 'ESTATE':
        target = state.inherited[move.player]
    if target in ['CARAVAN', 'FISHING VILLAGE', 'LIGHTHOUSE', 'MERCHANT SHIP',
                  'WHARF', 'AMULET', 'BRIDGE TROLL', 'CARAVAN GUARD',
                  'DUNGEON', 'HAUNTED WOODS', 'SWAMP HAG', 'ENCHANTRESS',
                  'COBBLER', 'DEN OF SIN', 'GHOST TOWN' 'GUARDIAN', 'RAIDER']:
        return 1

    elif target in ['CHAMPION', 'HIRELING']:
        return -1

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
    elif target in ['ARCHIVE', 'CRYPT', 'RESEARCH']:
        j = i + 1
        while j < len(moves) and moves[j].indent > moves[i].indent:
            secondary = moves[j]
            if secondary.indent == move.indent + 1 and \
                    secondary.pred == 'SET ASIDE':
                return len(secondary.items[0])
            j += 1
    elif target == 'SECRET CAVE':
        j = i + 1
        while j < len(moves) and moves[j].indent > moves[i].indent:
            secondary = moves[j]
            if secondary.indent == move.indent + 1 and \
                    secondary.pred == 'DISCARD' and \
                    len(secondary.items[0]) == 3:
                return 1
            j += 1
    else:
        return 0


def standard_plays(moves, i, blockLength, state):
    def deathcart_play(moves, i, blockLength, state):
        move = moves[i]
        if move.items[0].primary == 'DEATH CART' and \
                'DEATH CART' in state['INPLAYS'][move.player]:
            state.move(move.player, 'INPLAYS', 'TRASH', move.items[0])
        else:
            state.move(move.player, 'HANDS', 'TRASH', move.items[0])

    def hermit_trash(moves, i, blockLength, state):
        move = moves[i]
        if move.items[0].primary in state['DISCARDS'][move.player]:
            standard_trash('DISCARDS')(moves, i, blockLength, state)
        else:
            standard_trash('HANDS')(moves, i, blockLength, state)

    def smallcastle_trash(moves, i, blockLength, state):
        move = moves[i]
        if move.items[0].primary in state['HANDS'][move.player]:
            standard_trash('HANDS')(moves, i, blockLength, state)
        else:
            standard_trash('INPLAYS')(moves, i, blockLength, state)

    def monastery_trash(moves, i, blockLength, state):
        move = moves[i]
        inplayCoppers = state['INPLAYS'][move.player]['COPPER']
        trashCoppers = move.items[0]['COPPER']
        copperStack = Cardstack({'COPPER': min(inplayCoppers, trashCoppers)})
        state.move(move.player, 'INPLAYS', 'TRASH', copperStack)
        state.move(move.player, 'HANDS', 'TRASH', move.items[0] - copperStack)

    def knight_selfTrash(knight):
        def out_function(move):
            return move.pred == 'TRASH' and move.items[0].primary == knight
        return out_function

    def knight_oppTrash(knightPlayer):
        def out_function(move):
            return move.pred == 'TRASH' and move.player != knightPlayer
        return out_function

    def michael_discard(knightPlayer):
        def out_function(move):
            return move.pred == 'DISCARD' and move.player != knightPlayer
        return out_function

    move = moves[i]
    target = move.items[0].primary
    if target == 'ESTATE':
        target = state.inherited[move.player]
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
                'COUNTING HOUSE': [exc_settlers],
                'LOAN': [exc_revealDiscard, exc_revealTrash],
                'RABBLE': [exc_revealDiscard, exc_revealTopdeck],
                'VENTURE': [exc_revealDiscard,
                            Exception(check(['PLAY']), move_play('DECKS'))],
                'BAG OF GOLD': [gainTo('SUPPLY', 'DECKS')],
                'FARMING VILLAGE': [exc_revealDiscard],
                'FORTUNE TELLER': [exc_revealDiscard, exc_revealTopdeck],
                'HARVEST': [exc_revealDiscard],
                'HORN OF PLENTY': [exc_revealTrash],
                'HUNTING PARTY': [exc_revealDiscard],
                'JESTER': [exc_revealDiscard],
                'TOURNAMENT': [gainTo('SUPPLY', 'DECKS')],
                'CARTOGRAPHER': [exc_revealTopdeck, exc_revealDiscard],
                'DEVELOP': [gainTo('SUPPLY', 'DECKS')],
                'DUCHESS': [exc_revealTopdeck, exc_revealDiscard],
                'ILL-GOTTEN GAINS': [gainTo('SUPPLY', 'HANDS')],
                'JACK OF ALL TRADES': [exc_revealTopdeck, exc_revealDiscard],
                'NOBLE BRIGAND': [exc_revealTrash, exc_revealDiscard],
                'ORACLE': [exc_revealTopdeck, exc_revealDiscard],
                'ARMORY': [gainTo('SUPPLY', 'DECKS')],
                'BAND OF MISFITS': [Exception(check(['PLAY']),
                                              standard_plays)],
                'BEGGAR': [gainTo('SUPPLY', 'HANDS')],
                'CATACOMBS': [exc_revealDiscard],
                'COUNTERFEIT': [exc_inplayTrash],
                'DEATH CART': [Exception(check(['TRASH']), deathcart_play)],
                'GRAVEROBBER': [Exception(check(['GAIN TOPDECK']),
                                          standard_gains('TRASH', 'DECKS'))],
                'HERMIT': [Exception(check(['TRASH']), hermit_trash)],
                'IRONMONGER': [exc_revealDiscard, exc_revealTopdeck],
                'PILLAGE': [exc_inplayTrash],
                'REBUILD': [exc_revealTrash, exc_revealDiscard],
                'PROCESSION': [exc_inplayTrash],
                'ROGUE': [exc_revealTrash, exc_revealDiscard,
                          gainTo('TRASH', 'DISCARDS')],
                'SAGE': [exc_revealDiscard],
                'SCAVENGER': [exc_harbinger],
                'SURVIVORS': [exc_revealDiscard, exc_revealTopdeck],
                'VAGRANT': [exc_revealTopdeck],
                'WANDERING MINSTREL': [exc_revealDiscard, exc_revealTopdeck],
                'ADVISOR': [exc_revealDiscard],
                'BUTCHER': [Exception(check(['USE COFFER', 'USE COFFERS']),
                                      empty)],
                'DOCTOR': [exc_revealTrash, exc_revealDiscard,
                           exc_revealTopdeck],
                'HERALD': [Exception(check(['PLAY']), move_play('DECKS'))],
                'JOURNEYMAN': [exc_revealDiscard],
                'TAXMAN': [gainTo('SUPPLY', 'DECKS')],
                'ARTIFICER': [gainTo('SUPPLY', 'DECKS')],
                'COIN OF THE REALM': [checkMove(['PUT ONTO'],
                                                'INPLAYS', 'TAVERN')],
                'DISTANT LANDS': [checkMove(['PUT ONTO'],
                                            'INPLAYS', 'TAVERN')],
                'DUPLICATE': [checkMove(['PUT ONTO'], 'INPLAYS', 'TAVERN')],
                'GIANT': [exc_revealDiscard, exc_revealTrash],
                'GUIDE': [checkMove(['PUT ONTO'], 'INPLAYS', 'TAVERN')],
                'MAGPIE': [exc_revealTopdeck],
                'MISER': [checkMove(['PUT ONTO'], 'INPLAYS', 'TAVERN')],
                'RATCATCHER': [checkMove(['PUT ONTO'], 'INPLAYS', 'TAVERN')],
                'RAZE': [checkMove(['TRASH'], 'INPLAYS', 'TRASH', ['RAZE'])],
                'ROYAL CARRIAGE': [checkMove(['PUT ONTO'],
                                             'INPLAYS', 'TAVERN')],
                'TEACHER': [checkMove(['PUT ONTO'], 'INPLAYS', 'TAVERN')],
                'TRANSMOGRIFY': [checkMove(['PUT ONTO'],
                                           'INPLAYS', 'TAVERN')],
                'WARRIOR': [exc_revealDiscard,
                            checkMove(['TRASH'], 'DISCARDS', 'TRASH')],
                'WINE MERCHANT': [checkMove(['PUT ONTO'],
                                            'INPLAYS', 'TAVERN')],
                'SETTLERS': [exc_settlers],
                'BUSTLING VILLAGE': [exc_settlers],
                'GLADIATOR': [Exception(check(['TRASH']),
                                        standard_trash('SUPPLY'))],
                'SMALL CASTLE': [Exception(check(['TRASH']),
                                           smallcastle_trash)],
                "FARMERS' MARKET": [exc_inplayTrash],
                'OVERLORD': [Exception(check(['PLAY']), standard_plays)],
                'CHANGELING': [exc_inplayTrash],
                'SACRED GROVE': [Exception(check(['RECEIVE']),
                                           standard_boonhex(True))],
                'CRYPT': [checkMove(['SET ASIDE'], 'INPLAYS', 'OTHERS')],
                'MONASTERY': [Exception(check(['TRASH']), monastery_trash)],
                'NECROMANCER': [Exception(check(['PLAY']), standard_plays)],
                'NIGHT WATCHMAN': [exc_revealDiscard, exc_revealTopdeck],
                'TRAGIC HERO': [exc_inplayTrash],
                'MAGIC LAMP': [exc_inplayTrash],
                'GHOST': [exc_revealDiscard,
                          checkMove(['SET ASIDE'], 'DECKS', 'OTHERS')],
                'WISH': [gainTo('SUPPLY', 'HANDS')],
                'ZOMBIE MASON': [exc_revealTrash],
                'ZOMBIE SPY': [exc_revealDiscard, exc_revealTopdeck],
                'ENVOY': [exc_revealDiscard],
                'PRINCE': [checkMove(['SET ASIDE'], 'HANDS', 'OTHERS')],
                'ACTING TROUPE': [exc_inplayTrash],
                'BORDER GUARD': [exc_revealDiscard],
                'MOUNTAIN VILLAGE': [exc_settlers],
                'SCEPTER': [Exception(check(['PLAY']), standard_plays)],
                'SCULPTOR': [gainTo('SUPPLY', 'HANDS')],
                'SEER': [exc_revealTopdeck],
                'TREASURER': [gainTo('TRASH', 'HANDS')],
                'RESEARCH': [checkMove(['SET ASIDE'], 'DECKS', 'OTHERS')],
                }

    if target in triggers:
        for exc in triggers[target]:
            newExc = deepcopy(exc)
            newExc.lifespan = blockLength
            newExc.indents = [moves[i].indent + 1]
            state.exceptions.add(newExc)

    if target == 'REPLACE':
        for secondary in moves[i + 1: i + blockLength]:
            if secondary.pred == 'GAIN':
                def replace_topdeck(moves, i, blockLength, state):
                    block = Cardstack({target.primary: 1})
                    state.move(moves[i].player, get_gain_dest(target.primary),
                               'DECKS', block)

                newExc = Exception(check(['TOPDECK'],
                                         ['CARD', move.items[0].primary]),
                                   replace_topdeck)
                newExc.lifespan = blockLength
                newExc.indents = [secondary.indent + 1]
                state.exceptions.add(newExc)
                break

    elif target in ['BRIGE', 'INVENTOR']:
        state.bridges += 1

    elif target in ['THRONE ROOM', "KING'S COURT", 'DISCIPLE', 'CROWN']:
        plays = []
        for j in range(i + 1, i + blockLength):
            if moves[j].indent == moves[i].indent + 1 and \
                    moves[j].pred in playPreds:
                subject = moves[j].items[0].primary
                plays.append(j)
        if plays:
            state.linkedPlays.append([plays, Cardstack({target: 1,
                                                        subject: 1}), None])

    elif target == 'SCEPTER':
        if i + 1 < len(moves) and moves[i + 1].pred == 'PLAY':
            stayout = get_stayout_duration(moves, i + 1, state)
            subject = moves[i + 1].items[0].primary
            if stayout:
                # Look for something already going
                for j in range(len(state.linkedPlays)):
                    plays, cards, current = state.linkedPlays[j]
                    if current:
                        state.durations[moves[i].player].remove(current)
                        newDur = [cards, 1]
                        plays.append(i + 1)
                        cards['SCEPTER'] += 1
                        state.linkedPlays[j][2] = newDur
                        state.durations[moves[i].player].append(newDur)
                        return
                # Look for something minimal (not in linkedPlays)
                for j in range(0, i):
                    secondary = moves[j]
                    if check(['PLAY'], [subject])(secondary):
                        if len([x for x in state.linkedPlays
                                if j in x[0]]) == 0:
                            block = Cardstack({secondary: 1, 'SCEPTER': 1})
                            newDur = [block, 1]
                            state.linkedPlays.append([[j, i + 1], block,
                                                      newDur])
                            state.durations[moves[i].player].append(newDur)
                            return
                # Look for minimal in linkedPlays
                state.linkedPlays.sort(key=lambda x: len(x[1]))
                plays, cards, current = state.linkedPlays[0]
                state.durations[moves[i].player].remove(current)
                newDur = [cards, 1]
                plays.append(i + 1)
                cards['SCEPTER'] += 1
                state.linkedPlays[0][2] = newDur
                state.durations[moves[i].player].append(newDur)
                return
            else:
                # Look for something not already going
                for j in range(len(state.linkedPlays)):
                    plays, cards, current = state.linkedPlays[j]
                    if not current:
                        plays.append(i + 1)
                        cards['SCEPTER'] += 1
                        return
                # Look for something minimal (not in linkedPlays)
                for j in range(0, i):
                    secondary = moves[j]
                    if check(['PLAY'], [subject])(secondary):
                        if len([x for x in state.linkedPlays
                                if j in x[0]]) == 0:
                            block = Cardstack({secondary: 1, 'SCEPTER': 1})
                            state.linkedPlays.append([[j, i + 1], block, None])
                            return
                # Look for minimal in linkedPlays
                state.linkedPlays.sort(key=lambda x: len(x[1]))
                plays, cards, current = state.linkedPlays[0]
                state.durations[moves[i].player].remove(current)
                newDur = [cards, 1]
                plays.append(i + 1)
                cards['SCEPTER'] += 1
                state.linkedPlays[0][2] = newDur
                state.durations[moves[i].player].append(newDur)
                return

    elif target == 'STORYTELLER':
        state.coins = 0

    elif target == 'ENGINEER':
        if move.indent == 0:
            def engineer_trash(moves, i, blockLength, state):
                state.move(moves[i].player, 'INPLAYS', 'TRASH',
                           moves[i].items[0])
            exceptions = [Exception(check(['TRASH']),
                                    set_phase(engineer_trash),
                                    indents=[0],
                                    lifespan=blockLength + 1),
                          Exception(check(['GAIN']),
                                    set_phase(standard_gains('SUPPLY')),
                                    indents=[0],
                                    lifespan=blockLength + 2)]
        else:
            exceptions = [deepcopy(exc_inplayTrash)]
            exceptions[0].indents = [move.indent + 1]
            exceptions[0].lifespan = blockLength
        for exc in exceptions:
            state.exceptions.add(exc)

    elif target == 'PIXIE':
        exceptions = [Exception(check(['TRASH'], ['PIXIE']),
                                moveFunct('INPLAYS', 'TRASH'),
                                priority=2),
                      Exception(check(['TAKES']), standard_boonhex())]
        for exc in exceptions:
            exc.indents = [move.indent + 1]
            exc.lifespan = blockLength
            state.exceptions.add(exc)

    elif target == 'CARGO SHIP':
        state.cargoShips += 1

    elif target == 'IMPROVE':
        for life in range(1, len(moves) - i):
            if moves[life].pred == 'NEW TURN':
                break
        state.exceptions.add(Exception(check(['TRASH']),
                                       moveFunct('INPLAYS', 'TRASH'),
                                       lifespan=life,
                                       indents=[0]))

    if 'k' in Cards[target].types:
        for newExc in [Exception(knight_selfTrash(target),
                                 moveFunct('INPLAYS', 'TRASH')),
                       exc_revealDiscard,
                       Exception(knight_oppTrash(move.player),
                                 moveFunct('DECKS', 'TRASH'))]:
            newExc.lifespan = blockLength
            newExc.indents = [moves[i].indent + 1]
            state.exceptions.add(newExc)

        if target == 'SIR MICHAEL':
            newExc = Exception(michael_discard(move.player),
                               moveFunct('HANDS', 'DISCARDS'),
                               blockLength, [moves[i].indent + 1], 2)
            state.exceptions.add(newExc)

    stayout = get_stayout_duration(moves, i, state)
    inside = False
    if stayout:
        for index, data in enumerate(state.linkedPlays):
            plays, cards, current = data
            if i in plays:
                if current is None or stayout > current[1]:
                    if current:
                        state.durations[move.player].remove(current)
                    newDur = [cards, stayout]
                    state.durations[move.player].append(newDur)
                    state.linkedPlays[index][2] = newDur
                inside = True
                break

        if not inside:
            newDur = [Cardstack({target: 1}), stayout]
            state.linkedPlays.append([[i], Cardstack({target: 1}), newDur])
            state.durations[move.player].append(newDur)


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

    standard_plays(moves, i, blockLength, state)

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
                if life != 0:
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
    if state.phase == 4 and move.indent == 0 and \
            move.items[0].primary == 'FAITHFUL HOUND':
        state.move(move.player, 'OTHERS', 'HANDS', move.items[0])
    else:
        state.move(move.player, 'DECKS', 'HANDS', move.items[0])


Preds['PUT INHAND'].action = inhand_action


def inhand_generic_action(moves, i, blockLength, state):
    move = moves[i]
    if move.items[1].primary in ['HAVEN', 'GEAR', 'ARCHIVE', 'CRYPT']:
        state.move(move.player, 'OTHERS', 'HANDS', move.items[0])
    else:
        state.move(move.player, 'DECKS', 'HANDS', move.items[0])


Preds['INHAND GENERIC'].action = inhand_generic_action


def set_aside_action(moves, i, blockLength, state):
    move = moves[i]
    if 'b' not in move.items[0].primary:
        state.move(move.player, 'INPLAYS', 'OTHERS', move.items[0])


Preds['SET ASIDE'].action = set_aside_action

Preds['PUT ONTO'].action = moveFunct('HANDS', 'OTHERS')


def call_action(moves, i, blockLength, state):
    move = moves[i]
    target = move.items[0].primary
    if target == 'ESTATE':
        target = state.inherited[move.player]
    state.move(move.player, 'TAVERN', 'INPLAYS', move.items[0])
    # Barring some weird stuff like carriaging a werewolf/crown
    if move.indent == 0:
        state.phase = 1

    triggers = {'COIN OF THE REALM': [Exception(check(['ACTIONS GENERIC']),
                                                empty)],
                'DUPLICATE': [gainTo('SUPPLY', 'DISCARDS')],
                'TRANSMOGRIFY': [Exception(check(['GAIN']),
                                           standard_gains('SUPPLY', 'HANDS'),
                                           priority=2)],
                'ROYAL CARRIAGE': [Exception(check(['THRONE']),
                                             standard_plays)]
                }

    if target in triggers:
        for exc in triggers[target]:
            newExc = deepcopy(exc)
            newExc.action = set_phase(newExc.action)
            newExc.lifespan = blockLength + 1
            newExc.indents = [moves[i].indent]
            state.exceptions.add(newExc)

    def find_associated(moves, i):
        # Find carriage plays associated with the original play on
        # decision i
        turns = [i]
        for j in range(i + 1, len(moves)):
            if moves[j].indent <= moves[i].indent:
                break
            elif moves[j].pred == 'CALL' and \
                    moves[j].items[0].primary == 'ROYAL CARRIAGE' and \
                    moves[j].indent == moves[i].indent + 1:
                turns += find_associated(moves, j + 1)

        if moves[i].indent == 0:
            while j < len(moves):
                if moves[j].pred == 'CALL' and \
                        moves[j].items[0].primary == 'ROYAL CARRIAGE' and \
                        moves[j].indent == 0:
                    j += 1
                    turns += find_associated(moves, j)
                elif moves[j].indent == 0:
                    break
                j += 1

        return turns

    if target == 'ROYAL CARRIAGE':
        if move.indent == 0:
            for base in range(i - 1, 0, -1):
                if moves[base].pred in playPreds and \
                        moves[base].indent == 0:
                    break
        else:
            for base in range(i - 1, 0, -1):
                if moves[base].indent == move.indent - 1:
                    break

        inside = False
        for index in range(len(state.linkedPlays)):
            plays, cards, current = state.linkedPlays[index]
            if base in plays:
                plays.append(i + 1)
                cards['ROYAL CARRIAGE'] += 1
                if current:
                    newDur = [cards, current[1]]
                    state.durations[move.player].remove(current)
                    state.durations[move.player].append(newDur)
                    state.linkedPlays[index][2] = newDur
                inside = True
                break

        if not inside:
            subject = moves[base].items[0].primary
            stack = Cardstack({subject: 1, 'ROYAL CARRIAGE': 1})
            state.linkedPlays.append([[base, i + 1], stack, None])


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
            if life != 0:
                cleanable -= stack
        state.move(player, 'INPLAYS', 'DISCARDS', cleanable)
        state.move(player, 'HANDS', 'DISCARDS', state['HANDS'][player])

    state.move(player, 'DISCARDS', 'DECKS', state['DISCARDS'][player])


Preds['SHUFFLE'].action = shuffle_action


def return_to_action(moves, i, blockLength, state):
    move = moves[i]
    if move.items[0].primary == 'ENCAMPMENT':
        state.move(moves[i].player, 'OTHERS', 'SUPPLY', move.items[0])
    else:
        state.move(moves[i].player, 'INPLAYS', 'SUPPLY', move.items[0])


Preds['RETURN TO'].action = return_to_action


def return_action(moves, i, blockLength, state):
    move = moves[i]
    target = move.items[0].primary

    if 's' not in Cards[target].types:
        state.move(moves[i].player, 'INPLAYS', 'SUPPLY', move.items[0])


Preds['RETURN'].action = return_action


def standard_boonhex(grove=False):
    def out_function(moves, i, blockLength, state):
        move = moves[i]
        target = move.items[0].primary

        triggers = {'BAD OMENS': [checkMove(['TOPDECK'], 'DISCARDS', 'DECKS')],
                    'FAMINE': [exc_revealDiscard,
                               checkMove(['SHUFFLE INTO'], 'DECKS', 'DECKS'),
                               Exception(check(['SHUFFLE']), empty)],
                    'GREED': [gainTo('SUPPLY', 'DECKS')],
                    'LOCUSTS': [exc_revealTrash],
                    'PLAGUE': [gainTo('SUPPLY', 'HANDS')],
                    'WAR': [exc_revealDiscard, exc_revealTrash],
                    "THE MOON'S GIFT": [checkMove(['TOPDECK'], 'DISCARDS',
                                                  'DECKS')],
                    "THE SKY'S GIFT": [exc_revealDiscard, exc_revealTopdeck]
                    }
        if target in triggers:
            for exc in triggers[target]:
                newExc = deepcopy(exc)
                for life in range(1, len(moves) - i):
                    secondary = moves[i + life - 1]
                    if secondary.indent < move.indent:
                        break
                    elif not grove and (secondary.pred == 'DISCARD' and
                                        secondary.items[0].primary == target):
                        break
                newExc.lifespan = life
                newExc.indents = [moves[i].indent]
                newExc.persistent = True
                state.exceptions.add(newExc)
    return out_function


def receive_action(moves, i, blockLength, state):
    move = moves[i]
    target = move.items[0].primary

    if target in ['TREASURE HUNTER', 'WARRIOR', 'HERO', 'CHAMPION',
                  'SOLDIER', 'FUGITIVE', 'DISCIPLE', 'TEACHER', 'CHANGELING']:
        state.move(moves[i].player, 'SUPPLY', 'DISCARDS', move.items[0])
    elif 'b' in Cards[target].types:
        standard_boonhex()(moves, i, blockLength, state)


Preds['RETURN'].action = return_action
Preds['RECEIVE'].action = receive_action


def pass_action(moves, i, blockLength, state):
    move = moves[i]
    state['HANDS'][move.player] -= move.items[0]
    state['HANDS'][1 - move.player] += move.items[0]


Preds['PASS'].action = pass_action


def react_action(moves, i, blockLength, state):
    move = moves[i]
    target = move.items[0].primary
    exc = None
    if target == 'HORSE TRADERS':
        exc = Exception(check(['SET ASIDE']), moveFunct('HANDS', 'OTHERS'),
                        2, [move.indent])
    elif target == 'MARKET SQURE':
        exc = Exception(check(['DISCARD']), moveFunct('HANDS', 'DISCARDS'),
                        2, [move.indent])
    elif target == 'FAITHFUL HOUND':
        exc = Exception(check(['SET ASIDE']), moveFunct('DISCARDS', 'OTHERS'),
                        2, [move.indent])
    if exc:
        state.exceptions.add(exc)


Preds['REACT'].action = react_action


def genericVP(moves, i, blockLength, state):
    move = moves[i]
    state.vps[move.player] += int(move.arguments[0])


for p in ['SHIELD GAIN', 'SHIELD GET', 'SHIELD GENERIC']:
    Preds[p].action = genericVP


Preds['SET ASIDE WITH'].action = moveFunct('HANDS', 'OTHERS')


def take_coffers(moves, i, blockLength, state):
    move = moves[i]
    state.coffers[move.player] += int(move.arguments[0])


def single_coffers(moves, i, blockLength, state):
    move = moves[i]
    state.coffers[move.player] += 1


Preds['COFFERS GENERIC'].action = take_coffers
Preds['COFFER GENERIC'].action = take_coffers
Preds['GAIN COFFERS'].action = take_coffers
Preds['COFFERS FROM'].action = single_coffers


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


def take_action(moves, i, blockLength, state):
    move = moves[i]
    target = move.items[0]
    if target.primary in ['MISERABLE', 'TWICE MISERABLE']:
        state.vps[move.player] -= 2


Preds['TAKES'].action = take_action


def repay_debt(moves, i, blockLength, state):
    move = moves[i]
    if move.indent == 0:
        state.phase = 2
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
    target = move.items[0].primary
    state.obelisk = [target]

    sets = [['ENCAMPMENT', 'PLUNDER'],
            ['PATRICIAN', 'EMPORIUM'],
            ['SETTLERS', 'BUSTLING VILLAGE'],
            ['CATAPULT', 'ROCKS'],
            ['GLADIATOR', 'FORTUNE'],
            ['KNIGHTS', 'DAME ANNA', 'DAME JOSEPHINE', 'DAME MOLLY',
             'DAME NATALIE', 'DAME SYLVIA', 'SIR BAILEY', 'SIR DESTRY',
             'SIR MARTIN', 'SIR MICHAEL', 'SIR VANDER'],
            ['RUINS', 'RUINED LIBRARY', 'RUINED VILLAGE', 'ABANDONED MINE',
             'RUINED MARKET', 'SURVIVORS'],
            ['SAUNA', 'AVANTO']]

    for group in sets:
        if target == group[0]:
            state.obelisk = group


def inherit_action(moves, i, blocklength, state):
    move = moves[i]
    state.move(move.player, 'SUPPLY', 'OTHERS', move.items[0])
    state.inherited[move.player] = move.items[0].primary


Preds['OBELISK CHOICE'].action = obelisk_choice
Preds['INHERIT'].action = inherit_action


def enchant_action(moves, i, blocklength, state):
    for end in range(i + 1, len(moves)):
        if moves[end].indent < moves[i].indent:
            break

    enchantedExc = Exception(always, default_action, end - i + 1,
                             [moves[i].indent], 2, True)
    state.exceptions.add(enchantedExc)


Preds['ENCHANTED'].action = enchant_action

INTRINSIC_EXCEPTIONS = [defaultMove]
