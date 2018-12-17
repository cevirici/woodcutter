import re
from .classes import *
from .standards import *
from functools import reduce


def get_indent(line):
    t = re.search('padding-left:(.*?)em;', line).group(1)
    return int(float(t) // 1.5)


def get_card(name):
    for card in Cards:
        if name in Cards[card].names:
            return card
    return 'ARGUMENT'


def parse_card_phrase(cardlist):
    r = re.split(', | and ', cardlist)
    a = Cardstack({})

    for item in r:
        m = re.match('^(\d+|a|(?:an))? (.*)$', item)
        prefix = m.group(1)
        suffix = m.group(2)

        if prefix is None:
            card = get_card(suffix)
            if card == 'ARGUMENT':
                if re.match('^\d+$', suffix) is not None:
                    item[0] = int(suffix)
                a[card] = suffix
            else:
                a[card] = 0
        else:
            if prefix in ['a', 'an']:
                prefix = 1
            a[get_card(suffix)] = int(prefix)

    return a


def parse_line(line):
    indent = get_indent(line)
    line = re.sub('<.*?>|&bull;|&sdot;', '', line).strip()

    pred = Preds['OTHERS']
    for p in predParseOrder:
        if re.match(p.regex, line) is not None:
            pred = p
            break

    m = re.match(pred.regex, line)
    gd = m.groupdict()

    player = gd['player'] if 'player' in gd else None
    cards = parse_card_phrase(gd['cards']) if 'cards' in gd else Cardstack({})
    if 'argument' in gd:
        arg = '/'.join([gd[x] for x in ['argument', 'argument2'] if x in gd])
        cards['ARGUMENT'] = arg

    parsedLine = ParsedLine(player, indent, pred, cards)

    return parsedLine


def translate_file(inString):
    f = inString.split('~')
    parsedLog = []
    aliases = []
    players = {}

    for line in f:
        t = parse_line(line)
        if t.player:
            if t.pred == Preds['NEW TURN']:
                matchedAliases = [alias for alias in aliases if
                                  re.match('^' + alias, t.player) is not None]
                matchedAliases.sort(key=lambda x: -len(x))
                players[matchedAliases[0]] = t.player
                t.player = matchedAliases[0]
            else:
                if t.player not in aliases:
                    aliases.append(t.player)

                if t.pred == Preds['PASS']:
                    t.items['ARGUMENT'] = players[t.items['ARGUMENT']]

            t.player = aliases.index(t.player) + 1

        else:
            t.player = 0

        parsedLog.append(t)

    return parsedLog


def combined_parse(inStrings):
    logs = [translate_file(x) for x in inStrings]
    parsedLog = []
    gameNum = int(logs[0][0].items['ARGUMENT'].split('/')[0])

    actualLength = min([len(log) for log in logs])
    for i in range(actualLength):
        currentLine = [log[i] for log in logs]
        default = currentLine[0]

        passedItems = [pLn.items for pLn in currentLine if
                       ('CARD' not in pLn.items) and
                       ('NOTHING' not in pLn.items)
                       ]

        passedItems = reduce(lambda x, y: x.merge(y), passedItems)

        t = ParsedLine(default.player,
                       default.indent,
                       default.pred,
                       passedItems if passedItems else default.items
                       )

        parsedLog.append(repr(t))

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
