import copy

from .classes import *
from .standards import *

def unpack(logstring, supplystring):
    t = logstring.split('~')
    g = []
    for c in t:
        player = int(c[0:1], 16)-1
        indent = int(c[1:2], 16)
        pred = int(c[2:4], 16)
        cardString = c[4:]

        if len(cardString)>0:
            cards = [x.split(':') for x in cardString.split('|')]
            for card in cards:
                if int(card[1],16) != ARGUMENT_CARD:
                    card[0] = int(card[0])
            stack = Cardstack({int(x[1],16):x[0] for x in cards})
        else:
            stack = Cardstack({})

        g.append(ParsedLine(player,indent,pred,stack))

    t = supplystring.split('~')
    s = Cardstack({})
    for c in t:
        card = int(c[0:3],16)
        amount = int(c[3:5])
        s+=Cardstack({card:amount})

    return [g,s]

def parse_game(parsedLog):
    moveTree = []
    currentTurn = []
    lastIndent = 0
    indentBugDiff = 0
    indentBugThreshold = 0

    for i in range(len(parsedLog)):
        currentMove = parsedLog[i]
        if currentMove.pred == NEWTURN_PRED:
            moveTree.append(currentTurn)
            currentTurn = [currentMove]
            lastIndent = 0
        else:
            if currentMove.pred == currentMove.pred == GAMESTART_PRED:
                currentTurn = [currentMove]
            else:
                pointer = currentTurn
                #grrr
                if currentMove.indent > lastIndent + 1:
                    indentBugDiff = currentMove.indent - lastIndent - 1
                    indentBugThreshold = currentMove.indent
                elif currentMove.indent < indentBugThreshold:
                    indentBugDiff = 0

                for j in range(currentMove.indent - indentBugDiff):
                    pointer = pointer[-1]

                pointer.append([currentMove])
                lastIndent = currentMove.indent

    moveTree.append(currentTurn)

    return moveTree


index = 0
def get_decision_state(moveTree, supply):
    startState = gameState()
    startState.add(0, 'SUPPLY', supply)
    # Zombies
    if ZOMBIES[0] in supply:
        startState.move(0, 'SUPPLY', 'TRASH',
                        Cardstack({zombie: 1 for zombie in ZOMBIES}))

    gameStates = [startState]
    for turn in moveTree:
        turnExceptions = []
        def parse_chunk(chunk, exceptions, turnExceptions, persistents):
            subexceptions = []
            print(turnExceptions)
            global index
            print(index)
            index += 1
            gameStates.append(deepcopy(gameStates[-1]))

            passedExceptions = [exception for exception in exceptions + persistents
                                if exception.condition(chunk) == True]
            #One-time
            passedTurnExceptions = [exception for exception in turnExceptions if exception.condition(chunk) is True]

            if passedExceptions + passedTurnExceptions:
                for exception in passedExceptions + passedTurnExceptions:
                    exception.action(chunk, gameStates, subexceptions, turnExceptions, persistents)

                for exception in passedTurnExceptions:
                    turnExceptions.remove(exception)
            else:
                standardPreds[chunk[0].pred].action(chunk, gameStates, subexceptions, turnExceptions, persistents)

                for card in chunk[0].items:
                    if card != ARGUMENT_CARD:
                        for i in range(chunk[0].items[card]):
                            standardCards[card].action(chunk, gameStates, subexceptions, turnExceptions, persistents)

            for exception in turnExceptions:
                if exception.expiry > 0:
                    exception.expiry -= 1
                    if exception.expiry == 0:
                        turnExceptions.remove(exception)

            for subchunk in chunk[1:]:
                parse_chunk(subchunk, subexceptions, turnExceptions, persistents)

        parse_chunk(turn, [], turnExceptions, standardPersistents)

    return gameStates

def get_turn_points(moveTree):
    #Position of last decision in each turn, including the pregame turn
    def get_chunk_length(chunk):
        return sum([get_chunk_length(x) for x in chunk[1:]]) + 1
    lens = [get_chunk_length(chunk) for chunk in moveTree]
    return [sum(lens[:i+1])-1 for i in range(len(lens))]

def get_cleanup_points(moveTree):
    #Look for the first nonindented shuffle/draw
    def find_cleanup_chunk(chunk):
        if chunk[0].indent == 0 and chunk[0].pred in CLEANUP_PREDS:
            return 1
        else:
            t = -1
            for subchunk in chunk[1:]:
                if find_cleanup_chunk(subchunk) < 0:
                    t += find_cleanup_chunk(subchunk)
                else:
                    t = -t + find_cleanup_chunk(subchunk)
                    return t
            return t

    return [abs(find_cleanup_chunk(chunk)) for chunk in moveTree]

def get_turn_owners(moveTree):
    return [chunk[0].player for chunk in moveTree]

def get_shuffled_turns(moveTree):
    def had_shuffled(player, chunk):
        if chunk[0].pred == SHUFFLE_PRED and chunk[0].player == player:
            return True
        else:
            if [x for x in chunk[1:] if had_shuffled(player, x)]:
                return True
            else:
                return False

    return [[had_shuffled(p,x) for x in moveTree] for p in range(2)]

def get_involved_cards(gameStates):
    involvedCards = set()

    for state in gameStates:
        involvedCards.update(state.crunch(['DECKS','HANDS','INPLAYS','DISCARDS','OTHERS','TRASH'],[0,1]))

    involvedCards = list(involvedCards)
    involvedCards.sort()
    return involvedCards

def find_turn_decks(turnPoints, gameStates):
    turnDecks = [[] for i in range(2)]
    for point in turnPoints:
        for p in range(2):
            turnDecks[p].append(gameStates[point+1].crunch(['DECKS','HANDS','INPLAYS','DISCARDS','OTHERS'],[p]))

    return [turnDecks]

def find_gained_cards(turnPoints, gameStates):
    netGains = [[Cardstack({})] for i in range(2)]
    netTrashes = [[Cardstack({})] for i in range(2)]
    stepGains = [[Cardstack({})] for i in range(2)]

    for index in range(len(turnPoints) - 1):
        for p in range(2):
            startDeck = gameStates[turnPoints[index] + 1].crunch(
                        ['DECKS','HANDS','INPLAYS','DISCARDS','OTHERS'],[p])
            endDeck = gameStates[turnPoints[index + 1] + 1].crunch(
                      ['DECKS','HANDS','INPLAYS','DISCARDS','OTHERS'],[p])
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
    #subset?
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

            #Making sure active is a subset of the full deck
            diff = active - endDeck
            active = active - diff

            remainder = endDeck - active
            deck = remainder - discard
            discard = remainder - deck

            decks[p].append(deck)
            actives[p].append(active)
            discards[p].append(discard)

    return [discards, actives, decks]

def find_vp(turnPoints, gameStates):
    landmarks = ['Bandit Fort', 'Fountain', 'Keep', 'Museum', 'Obelisk',
                 'Orchard', 'Palace', 'Tower', 'Triumphal Arch', 'Wall', 'Wolf Den']

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
                if worth > 0:
                    currCounts.insert(card, rawDeck[card])
                    currWorths.insert(card, worth)

            landmarkVP = 0
            for cardscape in gameStates[point+1].SUPPLY[0] :
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
