from .classes import *
from .standards import *
from copy import deepcopy


def unpack(logString, supplyString):
    lines = logString.split('~')
    gL = []
    for line in lines:
        stack = Cardstack({})

        if len(itemString) > 0:
            items = [x.split(':') for x in itemString.split('|')]
            for item in items:
                cardName = str(CardList[int(item[1], 16)])
                quantity = item[0]
                if card != Card['ARGUMENT']:
                    quantity = int(quantity)
                stack[cardName] += quantity

        gL.append(ParsedLine(int(line[0:1], 16),  # Player
                             int(line[1:2], 16),  # Indent
                             PredList[int(line[2:4], 16)],  # Pred
                             stack))  # Items

    supplyItems = supplyString.split('~')
    supply = Cardstack({})
    for item in supplyItems:
        cardName = str(CardList[int(item[0:3], 16)])
        quantity = int(quantity[3:5])
        s[card] += quantity

    return (gL, supply)


def parse_gameLog(parsedLog):
    gameMoves = []
    blockLengths = []
    pointers = {}

    for line in parsedLog:
        if line.pred == Pred('GAME START') or line.pred == Pred('NEW TURN'):
            pointers[0] = len(gameMoves)
        else:
            pointers[line.indent + 1] = len(gameMoves)
            for i in range(line.indent + 1):
                blockLengths[pointers[i]] += 1

        gameMoves.append(line)
        blockLengths.append(1)

    tail = blockLengths[0]
    limit = len(gameMoves)
    while tail < limit:
        tail += blockLengths[tail]
        head = tail - 1
        indentCap = gameMoves[head].indent
        while gameMoves[head].indent <= indentCap and blockLengths[head] == 1:
            indentCap = min(gameMoves[head].indent, indentCap)
            gameMoves[head].isCleanup = True
            head -= 1

    return (gameMoves, blockLengths)


def parse_single_line(gM, i, bL, cS, activeExceptions):
    def updateExceptions(object, move, i, bL, gM, cS, t):
        a = object.action(move, i, bL, gM, cS)
        for exc in a:
            if exc.priority == 0:
                exc.priority = move.indent
            t[exc] = a[exc]

    move = gM[i]
    priorities = [exception.priority for exception in activeExceptions]
    pSorted = [[exc for exc in activeExceptions if exc.priority == p]
               for p in priorities]
    t = {}

    for layer in pSorted:
        triggered = False
        for exc in layer:
            if exc.condition(move):
                triggered = True
                updateExceptions(exc, move, i, bL, gM, currentState, t)
                if not exc.persistent:
                    del activeExceptions[exc]

        if triggered:
            break

    for exc in activeExceptions:
        activeExceptions[exc] -= 1
        if activeExceptions[exc] == 0:
            del activeExceptions[exc]

    if not triggered:
        updateExceptions(move.pred, move, i, bL, gM, currentState, t)
    for card in move.items.cardList():
        updateExceptions(card, move, i, bL, gM, currentState, t)

    activeExceptions.update(t)
    return (currentState, activeExceptions)


def parse_everything(gM, blockLengths, supply):
    # Setup starting state
    startState = GameState()
    for card in supply:
        if card not in DONT_LOAD:
            startState.add(0, 'SUPPLY', Cardstack({card: supply[card]}))

    if 'ZOMBIE APPRENTICE' in supply:
        zombieStack = Cardstack({z: 1 for z in ('ZOMBIE APPRENTICE',
                                                'ZOMBIE MASON',
                                                'ZOMBIE SPY')})
        startState.move(0, 'SUPPLY', 'TRASH', zombieStack)

    gameStates = [startState]
    aE = INTRINSIC_EXCEPTIONS
    for i, bL in enumerate(blockLengths):
        cS = deepcopy(gameStates[-1])

        (cS, aE) = parse_single_line(gM, i, bL, cS, copy(aE))
        gameStates.append(cS)

    return gameStates


def get_turn_points(blockLengths):
    # Position of last decision in each turn, including the pregame turn
    points = []
    pointer = 0
    while pointer < len(blockLengths):
        points.append(pointer)
        pointer += blockLengths[pointer]
    return points


def get_cleanup_points(gameMoves):
    return [i for i in range(1, len(gameMoves)) if
            gameMoves[i].isCleanup and not gameMoves[i - 1].isCleanup]


def get_turn_owners(gameMoves, turnPoints):
    return [gameMoves[i].player for i in turnPoints]


def get_shuffled_turns(gameMoves, turnPoints):
    outList = []
    for i in range(len(turnPoints) - 1):
        for scan in gameMoves[turnPoints[i]: turnPoints[i+1]]:
            if str(scan.pred) == 'SHUFFLE':
                outList.append(True)
                break
        outList.apend(False)
    return outList


def get_involved_cards(gameStates):
    involvedCards = set()

    for state in gameStates:
        involvedCards.update(state.crunch(PERSONAL_ZONES, (0, 1)))

    return list(involvedCards)


def find_gained_cards(turnPoints, gameStates):
    netGains = [[Cardstack({})] for i in range(2)]
    netTrashes = [[Cardstack({})] for i in range(2)]
    stepGains = [[Cardstack({})] for i in range(2)]

    for index in range(len(turnPoints) - 1):
        for p in range(2):
            startDeck = gameStates[turnPoints[index] + 1].crunch(
                        ['DECKS', 'HANDS', 'INPLAYS',
                         'DISCARDS', 'OTHERS'], [p])
            endDeck = gameStates[turnPoints[index + 1] + 1].crunch(
                      ['DECKS', 'HANDS', 'INPLAYS',
                       'DISCARDS', 'OTHERS'], [p])
            netGain = endDeck - startDeck
            netTrash = startDeck - endDeck

            stepGain = Cardstack({})

            for i in [turnPoints[index] + 1, turnPoints[index + 1]]:
                stepGain += gameStates[i+1].crunch(['DECKS','HANDS','INPLAYS','DISCARDS','OTHERS'],[p]
                            ) - gameStates[i].crunch(['DECKS','HANDS','INPLAYS','DISCARDS','OTHERS'],[p])

            stepGain = stepGain - netGain
            netGains[p].append(netGain)
            netTrashes[p].append(netTrash)
            stepGains[p].append(stepGain)

    return [netTrashes, stepGains, netGains]


def find_shuffle_progress(turnPoints, cleanupPoints, gameStates):
    # subset?
    turnPointsPlus = [-1] + turnPoints

    decks = [[] for i in range(2)]
    startingHands = [[] for i in range(2)]
    actives = [[] for i in range(2)]
    discards = [[] for i in range(2)]

    for index in range(len(turnPoints)):
        for p in range(2):
            endDeck = gameStates[cleanupPoints[index]].crunch(
                      ['DECKS','HANDS','INPLAYS','DISCARDS','OTHERS'],[p])
            discard = gameStates[cleanupPoints[index]].crunch(['DISCARDS'],[p])

            active = gameStates[turnPointsPlus[index] + 1].crunch(['HANDS','INPLAYS','OTHERS'], [p])

            for i in range(turnPointsPlus[index] + 1 , cleanupPoints[index]):
                active += gameStates[i + 1].crunch(['HANDS','INPLAYS','OTHERS'],[p] 
                          ) - gameStates[i].crunch(['HANDS','INPLAYS','OTHERS'],[p])

            # Making sure active is a subset of the full deck
            diff = active - endDeck
            active = active - diff

            remainder = endDeck - active
            deck = remainder - discard
            discard = remainder - deck

            decks[p].append(deck)
            actives[p].append(active)
            discards[p].append(discard)

    return [discards, actives, decks]


def find_vp(turnPoints, gameStates, rawSupply):
    vpCounts = [[] for i in range(2)]
    vpWorths = [[] for i in range(2)]
    for point in turnPoints:
        for p in range(2):
            rawDeck = gameStates[point+1].crunch(['DECKS', 'HANDS', 'INPLAYS',
                                                 'DISCARDS', 'OTHERS'], [p])
            currCounts = Cardstack({})
            currWorths = Cardstack({})
            for card in rawDeck:
                worth = standardCards[card].worth(gameStates[point+1], p)
                if worth != 0:
                    currCounts.insert(card, rawDeck[card])
                    currWorths.insert(card, worth)

            landmarkVP = 0
            for cardscape in rawSupply:
                if standardCards[cardscape].simple_name in landmarks:
                    landmarkVP += standardCards[cardscape].worth(gameStates[point+1], p)

            currCounts.insert(ARGUMENT_CARD, landmarkVP + gameStates[point+1].vps[p])

            vpCounts[p].append(currCounts)
            vpWorths[p].append(currWorths)

    return [vpCounts, vpWorths]


def full_printout(moveTree, gameStates):
    global index
    index = 0

    outfile = open('log.txt', 'w')

    def print_chunk(chunk, turnIndex):
        global index
        outfile.write('TURN {} \n'.format(turnIndex))
        outfile.write(str(index))
        outfile.write('{}>'.format('-'*chunk[0].indent))
        outfile.write(standardPreds[chunk[0].pred].name)
        outfile.write(chunk[0].items.debugstr())
        if not gameStates[index+1].valid:
            outfile.write("\n###INVALID MOVE")
        outfile.write(str(gameStates[index]))
        index += 1
        for subchunk in chunk[1:]:
            print_chunk(subchunk, turnIndex)

    turnIndex = 0
    for chunk in moveTree:
        print_chunk(chunk, turnIndex)
        turnIndex += 1
    outfile.close()


def get_empty_piles(supply, gameState):
    pass
