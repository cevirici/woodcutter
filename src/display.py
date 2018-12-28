from .Standards import *
import re


def get_passables():
    colors, borders, urls = [], [], []
    for card in Cardlist:
        colors.append(card.card_color)
        borders.append(card.border_color)
        urls.append(card.cardurl)
    return (colors, borders, names)


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
    data = [[players[x] for x in line.players],
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
