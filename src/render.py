from .classes import *

def makeDiv(classes, styles={}, otherAttrs={}, innerHTML=''):
    styleString = ' '.join(['{}: {};'.format(x, styles[x]) for x in styles])
    if styleString:
        styleString = ' style="{}"'.format(styleString)
    otherAttrString = ' '.join(['{}={}'.format(x, otherAttrs[x])
                                for x in otherAttrs])
    if innerHTML != '':
        innerHTML = '{}\n'.format(innerHTML.replace('\n', '\n\t'))

    baseString = '\n<div class=\'{}\'{} {}>{}</div>'
    return baseString.format(classes, styleString, otherAttrString, innerHTML)


class Tablebox:
    def __init__(self, card, classes, weight):
        self.card = card
        self.classes = classes
        self.weight = weight

    def __str__(self):
        bgUrlString = 'url("{}")'.format(self.card.cardurl)
        innerString = makeDiv('box-inner',
                              {'background-image': bgUrlString})

        borderColorString = "#{}".format(self.card.border_color)
        baseString = makeDiv('box ' + self.classes,
                             {'background': borderColorString},
                             {'card': self.card.index,
                              'weight': self.weight,
                              'pos': '\{\}'},
                             innerString)
        return baseString


class Tablesource:
    def __init__(self, columns, ordered):
        self.contents = [[[] for i in range(columns)] for j in range(2)]
        self.ordered = ordered
        self.involvedCards = []

    def __getitem__(self, item):
        return self.contents[item]

    def __str__(self):
        layerStrings = {card: '' for card in self.involvedCards}
        for side in range(2):



    def insert(self, player, column, cardstack):
        for item in cardstack:
            if item not in self.involvedCards:
                self.involvedCards.append(item)
            for i in range(cardstack[item]):
                self.contents[player][column].append(item)

    def setWeights(self, player, column, weights):
        self.weights[player][column].update(weights)


def make_turn_deck_table(turnPoints, gameStates):
    output = Tablesource(len(turnPoints), True)
    for i, point in enumerate(turnPoints):
        for p in range(2):
            deck = gameStates[point].crunch(PERSONAL_ZONES, [p])
            output.update(p, i, deck)

    return output
