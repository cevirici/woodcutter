from .Standards import *
import re


def get_passables():
    colors, borders, urls = [], [], []
    for card in CardList:
        colors.append(card.card_color)
        borders.append(card.border_color)
        urls.append(card.cardurl)
    return colors, borders, urls


def get_turn_owners(states):
    return [state.activePlayer for state in states]


def get_points(moves):
    stepPoints = []
    turnPoints = []
    for i, move in enumerate(moves):
        if move.pred == 'NEW TURN':
            turnPoints.append(i)
        if move.indent == 0:
            stepPoints.append(i)
    return stepPoints, turnPoints


def get_phases(states):
    return [state.phase for state in states]


def get_kingdom(supply):
    output = [[], [], []]
    pairs = {('DAME ANNA', 'DAME JOSEPHINE', 'DAME MOLLY', 'DAME NATALIE',
              'DAME SYLVIA', 'SIR BAILEY', 'SIR DESTRY', 'SIR MARTIN',
              'SIR MICHAEL', 'SIR VANDER'): 'KNIGHTS',
             ('RUINED LIBRARY', 'RUINED VILLAGE', 'ABANDONED MINE',
              'RUINED MARKET', 'SURVIVORS'): 'RUINS',
             ('HUMBLE CASTLE', 'CRUMBLING CASTLE', 'SMALL CASTLE',
              'HAUNTED CASTLE', 'OPULENT CASTLE', 'SPRAWLING CASTLE',
              'GRAND CASTLE', "KING'S CASTLE"): 'CASTLES'}
    for pair in pairs:
        if sum([supply[card] for card in pair]) > 1:
            output[Cards[pairs[pair]].supply_type].append(pairs[pair])

    for card in supply:
        if (supply[card] > 1 and Cards[card].supply_type != -1) or \
                Cards[card].supply_type == 2:
            output[Cards[card].supply_type].append(card)

    for n in range(len(output)):
        output[n].sort(key=lambda x: (Cards[x].cost, Cards[x].simple_name))

    return output


def get_inplays(states):
    return ['|'.join([str(Cards[card].index) for card in state.orderedPlays])
            for state in states]


def elaborate_card(number, card):
    if number == 1:
        return card.phrase_name
    elif number == 255:
        return card.simple_name
    else:
        return str(number) + ' ' + card.multi_name


def elaborate_cards(cardlist, fancy):
    if fancy:
        baseStr = "|{}|{}|"
        phrases = [baseStr.format(elaborate_card(cardlist[card], Cards[card]),
                                  Cards[card].index) for card in cardlist]
    else:
        phrases = [elaborate_card(cardlist[card], Cards[card])
                   for card in cardlist]

    if len(phrases) > 1:
        phrases[-1] = ' and ' + phrases[-1]
        for i in range(1, len(phrases) - 1):
            phrases[i] = ', ' + phrases[i]

    return ''.join(phrases)


def elaborate_line(players, line, fancy):
    if fancy:
        output = str(line.indent) + '>' + line.pred.regex
    else:
        output = '>' * line.indent + line.pred.regex
    playerFields = ('player', 'playerb')
    cardFields = ('cards', 'cardsb')
    argumentFields = ('argument', 'argumentb', 'argumentc')
    data = [['|{}|p{}|'.format(players[x], x) for x in line.players],
            [elaborate_cards(x, fancy) for x in line.items],
            line.arguments]

    for i, source in enumerate(data):
        for j, entry in enumerate(source):
            fieldName = [playerFields, cardFields, argumentFields][i][j]
            output = output.replace('(?P<{}>.*)'.format(fieldName), entry)

    output = re.sub(r'([^\\])[\.\(\)\+\$]', r'\1', output)
    output = re.sub(r'\\([\.\(\)\+\$])', r'\1', output)
    output = output.replace('^', '')

    return output


def elaborate_story(players, gameMoves, fancy=False):
    # Indents | Line | Owner | Turn Number
    return [elaborate_line(players, line, fancy) for line in gameMoves]
