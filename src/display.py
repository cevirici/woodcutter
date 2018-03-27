import re
from .classes import *
from .standards import *

from functools import reduce
from itertools import product

def makeDiv(classes, styles={}, otherAttrs={}, innerHTML=''):
    styleString = ' '.join(['{} : {};'.format(x, styles[x]) for x in styles])
    otherAttrString = ' '.join(['{} = {}'.format(x,otherAttrs[x]) for x in otherAttrs])
    if innerHTML != '':
        innerHTML = '{}\n'.format(innerHTML.replace('\n', '\n\t'))

    return '\n<div class = \'{}\'{}{}>{}</div>'.format(classes, 
                                                       ' style="{}"'.format(styleString) if styleString else '',
                                                       ' ' + otherAttrString if otherAttrString else '',
                                                       innerHTML)

def render_graph_row(stacks, styles, side):
    involvedCards = set()
    for stack in stacks:
        halfside = stack[side]
        for col in halfside:
            involvedCards.update(col.cardList())
    involvedCards = list(involvedCards)

    layerStrings = {}
    for card in involvedCards:
        layerStrings[card] = ''

    direction = ['bottom', 'top'][side]
    colHeights = [0 for i in range(len(stacks[0][0]))]

    for i in range(len(stacks)):
        stack = stacks[i]
        halfside = stack[side]
        for xpos in range(len(halfside)):
            col = halfside[xpos]
            colCards = sorted(col.cardList())

            for card in colCards:
                cardName = standardCards[card].simple_name
                cardColor = standardCards[card].card_color
                cardColorRGB = [int(cardColor[i:i+2], 16) for i in range(0, 6, 2)]
                cardLabel = ''.join([word[0] for word in cardName.split(' ')[:2]])
                isDark = sum(cardColorRGB) > 383

                for j in range(col[card]):
                    cardData = standardCards[card]
                    layerStrings[card] += \
                        makeDiv('box' + (' ' + styles[i] if styles[i] else ''),
                                {'background': '#{}'.format(cardData.border_color),
                                 direction: '{}vh'.format(1.75 * colHeights[xpos] + 0.5 * (colHeights[xpos]//5)),
                                 'left': '{}vh'.format(2.5 * xpos + 0.4)},
                                {'card': card,
                                 'side': 2 * (0.5 - side),
                                 'xcoord': xpos,
                                 'ycoord': colHeights[xpos],
                                 'currenty': colHeights[xpos]
                                 },
                                makeDiv('box-inner dark' if isDark else 'box-inner',
                                        styles={'background': '#{}'.format(cardData.card_color)},
                                        innerHTML=cardLabel
                                        )
                                )
                    colHeights[xpos] += 1

    for layer in layerStrings:
        layerStrings[layer] = makeDiv('graph-layer card' + str(layer), innerHTML=layerStrings[layer])

    return layerStrings.values()

def render_vp_row(vpCards, side):
    stack = vpCards[0]
    worths = vpCards[1]
    involvedCards = set()

    halfside = stack[side]
    for col in halfside:
        involvedCards.update(col.cardList())
    involvedCards = list(involvedCards)

    layerStrings = {ARGUMENT_CARD: ''}
    for card in involvedCards:
        layerStrings[card] = ''

    direction = ['bottom', 'top'][side]
    colHeights = [0 for i in range(len(stack[0]))]

    labelStrings = ''

    halfside = stack[side]
    for xpos in range(len(halfside)):
        col = halfside[xpos]
        colCards = sorted(col.cardList())
        rawvp = 0
        for card in colCards:
            if card != ARGUMENT_CARD:
                worth = worths[side][xpos][card]

                for j in range(col[card]):
                    cardData = standardCards[card]
                    passedBreaks = (colHeights[xpos] + worth - 1)//5 - colHeights[xpos]//5

                    layerStrings[card] += makeDiv('vpbox',
                                            {'background': '#{}'.format(cardData.border_color),
                                             direction: '{}vh'.format(1.3 * colHeights[xpos] + colHeights[xpos]//5 * 0.5),
                                             'left': '{}vh'.format(2.5 * xpos + 0.4),
                                             'height': '{}vh'.format(1.3 * worth - 0.3 + passedBreaks * 0.5)},
                                            {'card': card,
                                             'side': 2 * (0.5 - side),
                                             'xcoord': xpos,
                                             'ycoord': colHeights[xpos],
                                             'currenty': colHeights[xpos],
                                             'worth': worth
                                             },
                                             makeDiv('box-inner', styles={'background': '#{}'.format(cardData.card_color)})
                                             )
                    colHeights[xpos] += worth
            else:
                rawvp = int(col[card])

        if rawvp > 0:
            for j in range(rawvp):
                cardData = standardCards[ARGUMENT_CARD]
                passedBreaks = (colHeights[xpos] + 1)//5 - colHeights[xpos]//5

                layerStrings[ARGUMENT_CARD] += makeDiv('vpbox',
                                             {'background': '#191',
                                              direction: '{}vh'.format(1.3 * colHeights[xpos] + colHeights[xpos]//5 * 0.5),
                                              'left': '{}vh'.format(2.5 * xpos + 0.4),
                                              'height': '{}vh'.format(1)},
                                             {'card': ARGUMENT_CARD,
                                              'side': 2 * (0.5 - side),
                                              'xcoord': xpos,
                                              'ycoord': colHeights[xpos],
                                              'currenty': colHeights[xpos],
                                              'worth': 1
                                              },
                                              makeDiv('box-inner', styles={'background': '#494'})
                                              )
                colHeights[xpos] += 1
        else:
            for j in range(rawvp):
                cardData = standardCards[ARGUMENT_CARD]
                passedBreaks = colHeights[xpos]//5 - (colHeights[xpos] - 1)//5

                layerStrings[ARGUMENT_CARD] += makeDiv('vpbox',
                                             {'background': '#911',
                                              direction: '{}vh'.format(1.3 * (colHeights[xpos] - 1) + (colHeights[xpos]-1)//5 * 0.5),
                                              'left': '{}vh'.format(2.5 * xpos + 0.4),
                                              'height': '{}vh'.format(1)},
                                             {'card': ARGUMENT_CARD,
                                              'side': 2 * (0.5 - side),
                                              'xcoord': xpos,
                                              'ycoord': colHeights[xpos],
                                              'currenty': colHeights[xpos],
                                              'worth': 1
                                              },
                                              makeDiv('box-inner', styles={'background': '#944'})
                                              )
                colHeights[xpos] -= 1

        tot = sum([halfside[xpos][card] * worths[side][xpos][card] for card in
                  halfside[xpos] if card != ARGUMENT_CARD]) + rawvp
        labelStrings += makeDiv('vplabel',
                                {direction: '{}vh'.format(1.3 * colHeights[xpos] + (colHeights[xpos]-1)//5 * 0.5),
                                 'left': '{}vh'.format(2.5 * xpos)},
                                {},
                                str(tot))

    for layer in layerStrings:
        layerStrings[layer] = makeDiv('graph-layer card' + str(layer), innerHTML=layerStrings[layer])

    labelStrings = makeDiv('graph-layer', innerHTML=labelStrings)
    return [layerStrings.values(), labelStrings]


def render_graph_background(turnOwners, stripes, player):
    # Should Highlight | Should Stripe
    return [[turnOwners[i] == player, stripes[player][i]] for i in range(len(turnOwners))]

def render_axis_labels(turnOwners):
    axisLabels = ['||']
    t = 0
    for turn in range(1,len(turnOwners)):
        if turnOwners[turn] == 0 and turnOwners[turn-1] != 0:
            t += 1
        axisLabels.append(str(t)+'<br>'+'abcdef'[turnOwners[turn]])

    return axisLabels

def render_legend_boxes(involvedCards):
    # Name | Card Color | Border Color | Card Index
    legendBoxes = [[standardCards[card].simple_name,
                    standardCards[card].card_color,
                    standardCards[card].border_color,
                    card
                   ] for card in involvedCards]

    return legendBoxes

def render_story_sidebar_labels(turnOwners, turnPoints):
    # Turn | Label | Owner | Grow Amount
    sidebarLabels = [[0,'start', 1, 0]]

    t = 0
    for turn in range(1,len(turnOwners)):
        if turnOwners[turn] == 0 and turnOwners[turn-1] != 0:
            t += 1
        sidebarLabels.append([turn,
                              str(t) + 'abcdef'[turnOwners[turn]],
                              turnOwners[turn],
                              turnPoints[turn]-turnPoints[turn-1]
                              ])

    return sidebarLabels

def elaborate_cards(cardlist, fancy):
    phrases = []
    for item in cardlist:
        if item != ARGUMENT_CARD:
            thisCard = standardCards[item]
            thisPhrase = ''

            if cardlist[item] == 1:
                thisPhrase = thisCard.phrase_name
            elif cardlist[item] == 0:
                thisPhrase = thisCard.simple_name
            else:
                thisPhrase = '{} {}'.format(cardlist[item], thisCard.multi_name)

            if fancy:
                thisPhrase = "<div class='story-color' style='background: #{}; \
                               outline-color: #{};' card = {}>{}</div>".format(
                               thisCard.card_color, thisCard.border_color, item, thisPhrase)

            phrases.append(thisPhrase)

    if len(phrases) > 1:
        phrases[-1] = 'and ' + phrases[-1]

    return ', '.join(phrases)


def elaborate_story(players, moveTree):
    # Indents | Line | Owner | Turn Number
    lines = []
    rawlines = []

    def parseLine(entry):
        argumentsSplit = []

        if ARGUMENT_CARD in entry.items:
            argumentsSplit = entry.items[ARGUMENT_CARD].split('/')

        entryString = standardPreds[entry.pred].regex

        PLAYER_COLORS = ['#4277FE', '#FF4545']
        PLAYER_OUTLINES = ['#CECECE', '#CECECE']
        playerDiv = makeDiv('story-color',
                            {'background': PLAYER_COLORS[entry.player],
                             'outline-color': PLAYER_OUTLINES[entry.player]
                             },
                            innerHTML=players[entry.player])

        plainString = re.sub(r'\^?\(\?P<player>\.\*\)', players[entry.player], entryString)
        entryString = re.sub(r'\^?\(\?P<player>\.\*\)', playerDiv, entryString)

        elab = elaborate_cards(entry.items, True)
        plainElab = elaborate_cards(entry.items, False)
        if elab:
            entryString = re.sub(r'\(\?P<cards>(\.\*)\)', elab, entryString)
            plainString = re.sub(r'\(\?P<cards>(\.\*)\)', plainElab, plainString)
        elif argumentsSplit:
            if re.search(r'\(\?P<cards>(\.\*)\)', entryString) is not None:
                rightArgs = argumentsSplit.pop(0)
                entryString = re.sub(r'\(\?P<cards>(\.\*)\)', rightArgs, entryString)
                plainString = re.sub(r'\(\?P<cards>(\.\*)\)', rightArgs, plainString)

        entryString = reduce(lambda x, y: re.sub(r'\(\.\*\)', y, x, 1), argumentsSplit, entryString)
        entryString = re.sub(r'\\([\.\(\)\+])', r'\1', entryString)
        entryString = re.sub('\^|\$|\*', '', entryString)

        plainString = reduce(lambda x, y: re.sub(r'\(\.\*\)', y, x, 1), argumentsSplit, plainString)
        plainString = re.sub(r'\\([\.\(\)\+])', r'\1', plainString)
        plainString = re.sub('\^|\$|\*', '', plainString)

        return [entryString, plainString]

    def parseChunk(chunk, owner, turn):
        parsedChunk = parseLine(chunk[0])
        lines.append([(chunk[0].indent + 2) * 2, parsedChunk[0], owner, turn])
        rawlines.append(parsedChunk[1])

        for subchunk in chunk[1:]:
            parseChunk(subchunk, owner, turn)

    turn = 0
    for chunk in moveTree:
        parseChunk(chunk, chunk[0].player, turn)
        turn += 1

    return [lines, rawlines]

def render_kingdom(supply):
    # Kingdom | Nonsupply | Others (Cards)
    # Card | Index

    supplyCards = [standardCards[x] for x in supply]
    supplyCards = sorted(supplyCards, key=lambda x: (x.cost, x.simple_name))
    return [[[card, standardCards.index(card)] for
             card in supplyCards if card.supply_type == i] for i in range(3)]
