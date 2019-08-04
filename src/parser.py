import re
from .classes import *
from .Standards import *
from functools import reduce
from copy import deepcopy


def get_indent(line):
    t = re.search('padding-left:(.*?)em;', line).group(1)
    return int(float(t) // 1.5)


def get_card(name):
    for card in Cards:
        if name in Cards[card].names:
            return card


def parse_card_phrase(cardlist):
    r = re.split(', | and ', cardlist)
    a = Cardstack({})

    for item in r:
        m = re.match('^(?:(\d+|a|(?:an)) )?(.*)$', item)
        prefix, suffix = m.group(1), m.group(2)

        if prefix:
            if prefix in ['a', 'an']:
                prefix = 1
            a[get_card(suffix)] = int(prefix)
        else:
            a[get_card(suffix)] = 255

    return a


def parse_line(line):
    indent = get_indent(line)
    line = re.sub('<.*?>|&bull;|&sdot;', '', line).strip()
    line = re.sub('Kingdom generated with these relative precentages(.*)', '', line)
    for p in predParseOrder:
        if re.match(p.regex, line):
            pred = p
            break

    m = re.match(pred.regex, line)
    gd = m.groupdict()

    playerFields = ('player', 'playerb')
    players = [gd[group] for group in playerFields if group in gd]

    cardFields = ('cards', 'cardsb')
    cards = [parse_card_phrase(gd[group]) for group in cardFields
             if group in gd]

    argumentFields = ('argument', 'argumentb', 'argumentc')
    arguments = [gd[group] for group in argumentFields if group in gd]

    return ParsedLine(indent, pred, players, cards, arguments)


def translate_file(inString):
    lines = inString.split('~')
    parsedLog = []
    names = []

    for line in lines:
        parsed = parse_line(line)
        for i, player in enumerate(parsed.players):
            if parsed.pred == 'NEW TURN':
                matchedAliases = [name for name in names if
                                  re.match('^' + name, player)]
                matchedAliases.sort(key=lambda x: -len(x))
                if names.index(matchedAliases[0]) + 1 > 2:
                    print(player)
                parsed.players[i] = names.index(matchedAliases[0]) + 1
            else:
                if player not in names:
                    names.append(player)

                if names.index(player) + 1 > 2:
                    print(player)
                parsed.players[i] = names.index(player) + 1

        parsedLog.append(parsed)

    return parsedLog


def combined_parse(inStrings):
    logs = [translate_file(x) for x in inStrings]
    parsedLog = []
    gameNum = int(logs[0][0].arguments[0])

    actualLength = min([len(log) for log in logs])
    for i in range(actualLength):
        currentLines = [log[i] for log in logs]
        mergedLine = deepcopy(currentLines[0])
        mergedItems = [reduce(lambda x, y: x.merge(y),
                              [line.items[j] for line in currentLines])
                       for j in range(len(currentLines[0].items))]

        mergedLine.items = mergedItems

        parsedLog.append(repr(mergedLine))

    return ('~'.join(parsedLog), gameNum)


def parse_supply(inString):
    f = inString.split('~')
    cards = []

    baseStr = '{:0>3}{:0>2}'

    for line in f:
        entry = line.strip().rsplit("-", 1)
        for card in CardList:
            if entry[0] == card.simple_name:
                cards.append(baseStr.format(repr(card),
                                            entry[1]
                                            ))
                break

    return '~'.join(cards)
