import re
from .classes import *
from .standards import *

from functools import reduce
from django.contrib.staticfiles.templatetags.staticfiles import static


def makeDiv(classes, styles={}, otherAttrs={}, innerHTML=''):
    styleString = ' '.join(['{} : {};'.format(x, styles[x]) for x in styles])
    otherAttrString = ' '.join(['{} = {}'.format(x,otherAttrs[x]) for x in otherAttrs])
    if innerHTML != '':
        innerHTML = '{}\n'.format(innerHTML.replace('\n', '\n\t'))

    return '\n<div class = \'{}\'{}{}>{}</div>'.format(
                classes,
                ' style="{}"'.format(styleString) if styleString else '',
                ' ' + otherAttrString if otherAttrString else '',
                innerHTML)


def draw_graph_box(card, style, xpos, ypos, side, isDark,
                   borderColor, innerColor, label, height, baseheight, cardBG=''):
    direction = ['bottom', 'top'][side]
    actualY = (baseheight * 1.3) * ypos + 0.5 * (ypos//5)
    actualX = 2.5 * xpos + 0.4
    bgstring = 'background' if cardBG == '' else 'background-color'
    insideExtras = ''

    if 'redoutline' in style:
        insideExtras += makeDiv('redcover')

    boxString = makeDiv(style,
                        {'background': '{}'.format(borderColor),
                         direction: '{}vh'.format(actualY),
                         'left': '{}vh'.format(actualX),
                         'height': '{}vh'.format(height)
                         },
                        {'card': card,
                         'side': 2 * (0.5 - side),
                         'xcoord': xpos,
                         'ycoord': ypos,
                         'currenty': ypos
                         },
                        makeDiv('box-inner dark' if isDark else 'box-inner',
                                styles={bgstring: '{}'.format(innerColor),
                                        'background-image': 'url(\'{}\')'.format(static(cardBG))}
                                )
                        + insideExtras
                        )
    return boxString


def draw_standard_box(card, style, xpos, ypos, side, height=1.4, baseheight=1.4):
    cardData = standardCards[card]
    cardName = cardData.simple_name

    cardurlsplit = standardCards[card].cardurl.split(".")
    cardurlsplit[0] += '-tiny'
    cardBG = '.'.join(cardurlsplit)

    cardColor = '#{}'.format(cardData.card_color)
    borderColor = '#{}'.format(cardData.border_color)
    cardLabel = ''.join([word[0] for word in cardName.split(' ')[:2]])

    innerColorRGB = [int(cardColor[i:i+2], 16) for i in range(1, 7, 2)]
    isDark = sum(innerColorRGB) > 383

    return draw_graph_box(card, style, xpos, ypos, side, isDark,
                          borderColor, cardColor, cardLabel, height, baseheight,
                          cardBG)


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

    colHeights = [0 for i in range(len(stacks[0][0]))]

    for i in range(len(stacks)):
        stack = stacks[i]
        halfside = stack[side]
        for xpos in range(len(halfside)):
            col = halfside[xpos]
            colCards = sorted(col.cardList(), key=lambda x: card_order.index(
                                              standardCards[x].simple_name))

            for card in colCards:
                for j in range(col[card]):
                    fullStyle = 'box' + (' ' + styles[i] if styles[i] else '')
                    layerStrings[card] += draw_standard_box(
                        card, fullStyle, xpos, colHeights[xpos], side)
                    colHeights[xpos] += 1

    for layer in layerStrings:
        layerStrings[layer] = makeDiv('graph-layer card' + str(layer),
                                      innerHTML=layerStrings[layer])

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
    allPositiveCards = []
    allNegativeCards = []

    def getWorths(side, xpos, card):
        if card in worths[side][xpos]:
            return worths[side][xpos][card]
        else:
            return 0

    halfside = stack[side]
    for xpos in range(len(halfside)):
        col = halfside[xpos]

        colCards = sorted(col.cardList(), key=lambda x: card_order.index(
                                          standardCards[x].simple_name))
        positiveCards = [c for c in colCards if getWorths(side, xpos, c) > 0]
        negativeCards = [c for c in colCards if getWorths(side, xpos, c) < 0]
        rawvp = 0
        if ARGUMENT_CARD in colCards:
            rawvp = int(col[ARGUMENT_CARD])

        for card in positiveCards:
            worth = worths[side][xpos][card]
            for j in range(col[card]):
                cardData = standardCards[card]
                passedBreaks = (colHeights[xpos] + worth - 1)//5 - colHeights[xpos]//5
                cardHeight = 1.3 * worth - 0.3 + passedBreaks * 0.5

                layerStrings[card] += draw_standard_box(
                    card, 'vpbox', xpos, colHeights[xpos], side,
                    cardHeight, 1)
                colHeights[xpos] += worth

        if rawvp > 0:
            for j in range(rawvp):
                layerStrings[ARGUMENT_CARD] += draw_graph_box(
                    ARGUMENT_CARD, 'vpbox', xpos, colHeights[xpos], side,
                    False, '#119911', '#88BB88', '', 1, 1)

                colHeights[xpos] += 1

        tot = sum([halfside[xpos][card] * worths[side][xpos][card] for card in
                  halfside[xpos] if card != ARGUMENT_CARD]) + rawvp
        labelStrings += makeDiv('vplabel',
                                {direction: '{}vh'.format(0.5 + 1.3 * colHeights[xpos] +
                                                          (colHeights[xpos]-1)//5 * 0.5),
                                 'left': '{}vh'.format(2.5 * xpos)},
                                {},
                                str(tot))

        for card in negativeCards:
            worth = worths[side][xpos][card]
            for j in range(col[card]):
                cardData = standardCards[card]
                passedBreaks = (colHeights[xpos] - 1)//5 - (colHeights[xpos] + worth)//5
                cardHeight = 1.3 * (- worth) - 0.3 + passedBreaks * 0.5

                def stripeyGradient(color):
                    RGB = [int(color[i:i+2], 16) for i in range(0, 6, 2)]
                    rgbString = 'rgba({}, {}, {}, '.format(RGB[0], RGB[1], RGB[2])
                    return "repeating-linear-gradient(45deg, {}1), {}1) 10%,\
                    {}0) 10%,  {}0) 15%);".format(
                        rgbString, rgbString, rgbString, rgbString)

                if colHeights[xpos] > 0:
                    borderGradient = stripeyGradient(cardData.border_color)
                    innerGradient = stripeyGradient(cardData.card_color)

                    layerStrings[card] += draw_graph_box(
                        card, 'vpbox', xpos, colHeights[xpos] - 1, side,
                        False, borderGradient, innerGradient, '', cardHeight, 1)
                colHeights[xpos] += worth

        if rawvp < 0:
            for j in range(rawvp):
                layerStrings[ARGUMENT_CARD] += draw_graph_box(
                    ARGUMENT_CARD, 'vpbox', xpos, colHeights[xpos], side,
                    False, '#991199', '#BB88BB', '', 1, 1)

                colHeights[xpos] -= 1

        allPositiveCards += [card for card in positiveCards if
                             card not in allPositiveCards]
        allNegativeCards += [card for card in negativeCards if
                             card not in allNegativeCards]

    for layer in layerStrings:
        layerStrings[layer] = makeDiv('graph-layer card' + str(layer),
                                      innerHTML=layerStrings[layer])

    sortedStrings = [layerStrings[card] for card in allPositiveCards]
    if ARGUMENT_CARD in layerStrings:
        sortedStrings.append(layerStrings[ARGUMENT_CARD])
    sortedStrings += [layerStrings[card] for card in allNegativeCards]

    labelStrings = makeDiv('graph-layer', innerHTML=labelStrings)
    return [sortedStrings, labelStrings]


def render_graph_background(turnOwners, stripes, player):
    # Should Highlight | Should Stripe
    return [[turnOwners[i] == player, stripes[player][i]] for i in range(len(turnOwners))]


def render_axis_labels(turnOwners):
    axisLabels = ['||']
    t = 0
    for turn in range(1, len(turnOwners)):
        if turnOwners[turn] == 0 and turnOwners[turn-1] != 0:
            t += 1
        axisLabels.append(str(t)+'<br>'+'abcdef'[turnOwners[turn]])

    return axisLabels


def render_legend_boxes(involvedCards):
    # Name | Card Color | Border Color | Card Index
    legendBoxes = [[standardCards[card].simple_name,
                    standardCards[card].cardurl,
                    standardCards[card].border_color,
                    card,
                    standardCards[card].card_color,
                    ] for card in involvedCards]
    legendBoxes.sort(key=lambda x: card_order.index(x[0]))
    return legendBoxes


def render_story_sidebar_labels(turnOwners, turnPoints):
    # Turn | Label | Owner | Grow Amount
    sidebarLabels = [[0, 'start', 1, 0]]

    t = 0
    for turn in range(1, len(turnOwners)):
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
        if item != 'ARGUMENT':
            thisCard = Cards[item]
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
        phrases[-1] = ' and ' + phrases[-1]
        for i in range(1, len(phrases) - 1):
            phrases[i] = ', ' + phrases[i]

    return ''.join(phrases)


def elaborate_line(players, entry):
    PLAYER_COLORS = ['#FF4545', '#4277FE']
    PLAYER_OUTLINES = ['#CECECE', '#CECECE']

    regexCard = r'\(\?P<cards>(\.\*)\)'

    entryString = entry.pred.regex
    argumentsSplit = []

    if 'ARGUMENT' in entry.items:
        argumentsSplit = entry.items['ARGUMENT'].split('/')

    # Masq Story Exception
    if entry.pred == 'PASS':
        argumentsSplit[0] = players[int(argumentsSplit[0]) - 1]

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
        entryString = re.sub(regexCard, elab, entryString)
        plainString = re.sub(regexCard, plainElab, plainString)
    elif argumentsSplit:
        for regex in [regexCard, regexArg, regexArgB]:
            if re.search(regex, entryString) is not None:
                arg = argumentsSplit.pop(0)
                entryString = re.sub(regex, arg, entryString)
                plainString = re.sub(regex, arg, plainString)

    entryString = re.sub(r'\\([\.\(\)\+])', r'\1', entryString)
    entryString = re.sub('\^|\$|\*', '', entryString)
    plainString = re.sub(r'\\([\.\(\)\+])', r'\1', plainString)
    plainString = re.sub('\^|\$|\*', '', plainString)
    plainString = ">" * entry.indent + plainString

    return [entryString, plainString]


def elaborate_story(players, gameMoves, turnPoints):
    # Indents | Line | Owner | Turn Number
    lines = []
    rawlines = []

    turn = 0
    for i, move in enumerate(gameMoves):
        if turn < len(turnPoints):
            if i > turnPoints[turn]:
                turn += 1
        data = elaborate_line(players, move)
        lines.append([(move.indent + 2) * 2, data[0], turn])
        rawlines.append(data[1])

    return [lines, rawlines]


def render_kingdom(supply):
    # Kingdom | Nonsupply | Others (Cards)
    # Card | Index

    supplyCards = [standardCards[x] for x in supply if supply[x] > 1]
    supplyScapes = [standardCards[x] for x in supply if standardCards[x].simple_name in landscapes]
    supplyCards += supplyScapes

    for bunch in bunchCards:
        bunchCount = len([card for card in bunch[0] if card in supply])
        if bunchCount > 1:
            supplyCards.insert(0, standardCards[bunch[1]])

    supplyCards = sorted(supplyCards, key=lambda x: (x.cost, x.simple_name))
    return [[[card, standardCards.index(card)] for
             card in supplyCards if card.supply_type == i] for i in range(3)]


def exportGameStates(gameStates):
    return [gameState.export() for gameState in gameStates]


def relevantColors(supply):
    return {card: [standardCards[card].card_color,
                   standardCards[card].border_color,
                   standardCards[card].simple_name,
                   static(standardCards[card].cardurl)] for card in supply}
