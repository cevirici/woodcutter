from .classes import *
from copy import copy, deepcopy


def unpackCardstack(cardString):
    stack = Cardstack({})
    for chunk in cardString.split('+'):
        quantity, index = chunk.split(':')
        stack[str(CardList[int(index, 16)])] += int(quantity)
    return stack


def unpack(logString, supplyString):
    lines = logString.split('~')
    parsedLines = []

    for line in lines:
        indent, pred, rawPlayers, rawItems, rawArguments = line.split('|')
        indent = int(indent)
        pred = PredList[int(pred, 16)]
        players = [int(x) - 1 for x in rawPlayers.split('/')] if rawPlayers \
            else []
        items = [unpackCardstack(x) for x in rawItems.split('/')] \
            if rawItems else []
        arguments = rawArguments.split('/') if rawArguments else []

        parsedLines.append(ParsedLine(indent, pred, players, items, arguments))

    supplyItems = supplyString.split('~')
    supply = Cardstack({})
    for item in supplyItems:
        cardName = str(CardList[int(item[0:3], 16)])
        quantity = int(item[3:5])
        supply[cardName] += quantity

    return (parsedLines, supply)


def get_blocklengths(parsedLog):
    blockLengths = []
    pointers = {}
    for i, line in enumerate(parsedLog):
        if line.pred in ['GAME START', 'NEW TURN']:
            pointers[0] = i
        else:
            pointers[line.indent + 1] = i
            for j in range(line.indent + 1):
                blockLengths[pointers[j]] += 1

        blockLengths.append(1)

    return blockLengths


def get_vps(state, kingdom):
    output = []
    totals = []
    landmarks = [card for card in kingdom if 'l' in Cards[card].types]
    for player in range(len(state['DECKS'])):
        playerDeck = state.crunch(GameState.playerZones, [player])
        entries = [[0,
                    Cards[card].worth(state, player),
                    Cards[card].index] for card in playerDeck
                   if Cards[card].worth(state, player) != 0]
        entries += ([[1, Cards[card].worth(state, player),
                      Cards[card].index] for card in landmarks
                     if Cards[card].worth(state, player) != 0])
        if state.vps[player] != 0:
            entries.append([1, state.vps[player], 1])

        entries.sort(key=lambda x: x[2])
        output.append(entries)
        totals.append(str(sum([entry[0] * entry[1] for entry in entries])))

    return ['/'.join(['|'.join([str(x) for x in entry])
                      for entry in playerLine])
            for playerLine in output], totals
