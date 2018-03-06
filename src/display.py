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
	# Layer: Card Index | Cards as List

	# Other Classes | Border Color | Direction String
	# Card Index | Side | XCoord | YCoord | Inner Color
	# Y Position | X Position

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
				for j in range(col[card]):
					cardData = standardCards[card]
					layerStrings[card] += makeDiv('box'+(' ' + styles[i] if styles[i] else ''),
					                    	{'background' : '#{}'.format(cardData.border_color),
					                         direction : '{}vh'.format(1.75 * colHeights[xpos] + 0.5 * (colHeights[xpos]//5)),
					                         'left' : '{}vh'.format(2.5 * xpos + 0.4)},
					                        {'card' : card,
					                         'side' : 2 * (0.5 - side),
					                         'xcoord' : xpos,
					                         'ycoord' : colHeights[xpos],
					                         'currenty' : colHeights[xpos]
					                         },
					                         makeDiv('box-inner', styles = {'background' : '#{}'.format(cardData.card_color)})
					                         )
					colHeights[xpos] += 1

	for layer in layerStrings:
		layerStrings[layer] = makeDiv('graph-layer card' + str(layer), innerHTML = layerStrings[layer])

	return layerStrings.values()

def render_graph_background(turnOwners, stripes, player):
	# Should Highlight | Should Stripe
	return [[turnOwners[i] == player, stripes[player][i]] for i in range(len(turnOwners))]

def render_axis_labels(turnOwners):
	axisLabels = ['||']
	t = 0
	for turn in range(1,len(turnOwners)):
		if turnOwners[turn] == 0:
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
		if turnOwners[turn] == 0:
			t += 1
		sidebarLabels.append([turn,
			                  str(t) + 'abcdef'[turnOwners[turn]],
			                  turnOwners[turn],
			                  turnPoints[turn]-turnPoints[turn-1]
			                  ])

	return sidebarLabels

def elaborate_cards(cardlist):
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
				thisPhrase = '{} {}'.format(cardlist[item],thisCard.multi_name)

			thisPhrase = "<div class='story-color' style='background : #{}; \
			               outline-color : #{};' card = {}>{}</div>".format(
			               thisCard.card_color, thisCard.border_color, item, thisPhrase)

			phrases.append(thisPhrase)

	if len(phrases) > 1:
		phrases[-1] = 'and ' + phrases[-1]

	return ', '.join(phrases)

def elaborate_story(players, moveTree):
	# Indents | Line | Owner | Turn Number
	lines = []
	def parseLine(entry):
		argumentsSplit = []

		if ARGUMENT_CARD in entry.items:
			argumentsSplit = entry.items[ARGUMENT_CARD].split('/')

		entryString = standardPreds[entry.pred].regex
		entryString = re.sub(r'\^?\(\?P<player>\.\*\)',players[entry.player],entryString)

		elab = elaborate_cards(entry.items)
		if elab:
			entryString = re.sub(r'\(\?P<cards>(\.\*)\)', elab, entryString)
		elif argumentsSplit:
			if re.search(r'\(\?P<cards>(\.\*)\)', entryString) != None:
				entryString = re.sub(r'\(\?P<cards>(\.\*)\)', argumentsSplit.pop(0), entryString)

		entryString = reduce(lambda x,y: re.sub(r'\(\.\*\)',y,x,1), argumentsSplit,entryString)

		entryString = re.sub(r'\\([\.\(\)])',r'\1',entryString)
		entryString = re.sub('\^|\$|\*','',entryString)

		return entryString

	def parseChunk(chunk, owner, turn):
		lines.append([(chunk[0].indent + 2) * 2, parseLine(chunk[0]), owner, turn])

		for subchunk in chunk[1:]:
			parseChunk(subchunk, owner, turn)

	turn = 0
	for chunk in moveTree:
		parseChunk(chunk, chunk[0].player, turn)
		turn += 1

	return lines

def render_kingdom(supply):
	# Kingdom | Nonsupply | Others (Cards)
	# Card | Index

	supplyCards = [standardCards[x] for x in supply]
	supplyCards = sorted(supplyCards, key = lambda x: (x.cost, x.simple_name))
	return [[[card, standardCards.index(card)] for 
	          card in supplyCards if card.supply_type == i] for i in range(3)]