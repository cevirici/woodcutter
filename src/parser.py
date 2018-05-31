import re
from functools import reduce
from .classes import *
from .standards import *
import copy


def get_indent(line):
    t = re.search('padding-left:(.*?)em;', line).group(1)
    return int(float(t)//1.5)


def get_card(name):
    res = [i for i in range(len(standardCards)) if
           name in standardCards[i].names()]

    if res:
        return res[0]
    else:
        print('Unknown card {} found'.format(name))
        return ARGUMENT_CARD


def parse_card_phrase(cardlist):
    r = re.split(', | and ', cardlist)
    a = Cardstack({})

    for item in r:
        item = item.split(' ', 1)
        if len(item) == 2:
            if re.match('^\d+$|^an?$', item[0]) is not None:
                if item[0] in ['a', 'an']:
                    item[0] = 1

                item[0] = int(item[0])
            else:
                item[1] = ' '.join(item)
                item[0] = 0

            item[1] = get_card(item[1])

            a.insert(item[1], item[0])
        else:
            match = get_card(item[0])
            if match == ARGUMENT_CARD:
                if re.match('^\d+$', item[0]) is not None:
                    item[0] = int(item[0])
                a.insert(match, item[0])
            else:
                a.insert(match, 0)

    return a


def parse_line(line):
    indent = get_indent(line)
    line = re.sub('<.*?>|&bull;|&sdot;', '', line)
    line = line.strip()

    parsedLine = parse_line_contents(line)
    parsedLine.indent = indent

    return parsedLine


def parse_line_contents(line):
    pred = standardPreds[-1]
    for predIndex in pred_parse_order:
        if re.match(standardPreds[predIndex].regex, line) is not None:
            pred = standardPreds[predIndex]
            break

    m = re.match(pred.regex, line)
    player = -1
    lowlim = 3
    try:
        player = m.group('player')
    except BaseException:
        lowlim -= 1

    cards = Cardstack({})
    try:
        c_raw = m.group('cards')
        cards = parse_card_phrase(c_raw)
    except BaseException:
        lowlim -= 1

    for i in range(lowlim, len(m.groups())+1):
        cards.insert(ARGUMENT_CARD, m.group(i))

    parsedLine = ParsedLine(player, 0, pred, cards)

    return parsedLine


def translate_file(inString):
    f = inString.split('~')
    a = []
    player_list = ['GameStart']
    backup_player = 'GameStart'
    for line in f:
        t = parse_line(line)

        # Player handling - special exception for 'Turn n' pred,
        # because that uses long names.

        if t.player == -1:
            t.player = backup_player
        else:
            if t.pred != standardPreds[NEWTURN_PRED]:
                if t.player not in player_list:
                    player_list.append(t.player)
            else:
                match_names = [player for player in player_list if
                               re.match('^'+player, t.player) is not None]
                match_names.sort(key=lambda x: -len(x))
                t.player = match_names[0]

        # Masq Pass exception
        if t.pred.name == "PASS":
            target = t.items[ARGUMENT_CARD]
            match_names = [player for player in player_list if
                           re.match('^'+player, target) is not None]
            match_names.sort(key=lambda x: -len(x))
            t.items.val[ARGUMENT_CARD] = player_list.index(match_names[0])

        backup_player = t.player
        t.player = player_list.index(t.player)
        a.append(t)
    return [a, len(player_list)]


def combined_parse(inStrings):
    raws = [translate_file(x) for x in inStrings]
    a = []
    logs = [x[0] for x in raws]
    gameNum = int(logs[0][0].items[ARGUMENT_CARD].split('/')[0])

    for i in range(min([len(log) for log in logs])):
        t = [x[i] for x in logs]
        combined = copy.copy(t[0])

        candidate_items = [s_t.items for s_t in t]

        while len(candidate_items) > 1:
            candidate_items[0] = candidate_items[0].merge(candidate_items[-1])
            del candidate_items[-1]

        if len(candidate_items) > 0:
            combined.items = candidate_items[0]
        combined.player = hex(combined.player)[2:]
        combined.indent = hex(combined.indent)[2:]
        combined.pred = '{:0>2}'.format(hex(standardPreds
                                            .index(combined.pred))[2:])
        a.append(str(combined))

    outstr = '~'.join(a)
    return [outstr, gameNum]


def parse_supply(inString):
    f = inString.split('~')
    cards = []

    for line in f:
        r = line.strip().rsplit("-", 1)
        card = get_card(r[0])
        quant = '{:0>2}'.format(r[1])
        cards.append('{:0>3}'.format(hex(card)[2:])+quant)

    outstr = '~'.join(cards)
    return outstr
