import re
from .cardstack import Cardstack

from copy import deepcopy
from ceviri_net.settings import BASE_DIR
from functools import reduce
from itertools import product


def unpack(logstring, supplystring):
	t = logstring.split('~')
	g = []
	for c in t:
		player = int(c[0:1], 16)
		indent = int(c[1:2], 16)
		pred = int(c[2:4], 16)
		cardString = c[4:]
		if len(cardString)>0:
			cards = [x.split(':') for x in cardString.split('|')]
			for card in cards:
				if int(card[1],16) != 4095:
					card[0] = int(card[0])
			stack = Cardstack({int(x[1],16):x[0] for x in cards})
		else:
			stack = Cardstack({})
		g.append([player,indent,pred,stack])

	t = supplystring.split('~')
	s = Cardstack({})
	for c in t:
		card = int(c[0:3],16)
		amount = int(c[3:5])
		s+=Cardstack({card:amount})

	return [g,s]

class Renderer:
	def __init__(self,preds,cards):

		self.preds = []
		for pred in preds:
			self.preds.append([pred.regex,pred.source,pred.destination])

		self.cards = []
		self.cardPrimaries = []
		self.costs = []
		self.cardcolors = []
		self.bordercolors = []
		self.exceptions = []
		self.supplytypes = []

		for card in cards:
			self.cards.append([card.single_name,card.multi_name,card.phrase_name])
			self.cardPrimaries.append(card.single_name)
			self.costs.append(card.cost)
			self.cardcolors.append(card.color)
			self.bordercolors.append(card.border_color)
			self.exceptions.append(card.exceptions.all())
			self.supplytypes.append(card.supply_type)


		'''f = open(BASE_DIR+'/woodcutter/'+exceptionfilename,'r')
		self.exceptions = []
		for line in f:
			if line.strip():
				t = [[[int(z) for z in y.split('-')] for 
							y in x.split(',')] for 
								x in line.strip().split('||')]
			else:
				t = []
			self.exceptions.append(t) 
		f.close()'''

	def move_stuff(self, state, source, dest, player, items):
		if source != dest:
			srclist = state[source][min(player,len(state[source])-1)]
			destlist = state[dest][min(player,len(state[dest])-1)]

			if items.val == {}:
				items = deepcopy(srclist)
			
			if (items - srclist).cardList() == []:
				destlist += items
				srclist -= items
			else:
				print("Illegal move: {} from {} ({}) to {}".format(items, source, srclist, dest))

			state[source][min(player,len(state[source])-1)] = srclist
			state[dest][min(player,len(state[dest])-1)] = destlist

		return state

	def parse_game(self, parsedLog, supply, playerCount):
		l = [1,playerCount,playerCount,1,playerCount,playerCount,playerCount]

		gameState = []
		for i in l:
			t = []
			for x in range(i):
				t.append(Cardstack({}))
			gameState.append(t)

		gameState[0][0] += supply
		completeState = [gameState]
		turnBreaks = [[] for i in range(playerCount)]
		shuffles = [[] for i in range(playerCount)]
		indentTree = []

		turncount = 0
		for i in range(len(parsedLog)):
			line = parsedLog[i]

			player = line[0]-1
			indent = line[1]
			pred = line[2]
			predData = self.preds[pred]
			items = deepcopy(line[3])

			#Clear indentTree if it's the end of the turn.
			if pred == 1:
				indentTree = []

			#Populate indentTree
			indentTree = indentTree[:indent]
			indentTree.append(line)

			#Exceptional cases - if draw, but next thing is shuffle.
			if pred == 21:
				if i < len(parsedLog) -1:
					if parsedLog[i-1][2] == 46:
						d = 1
					else:
						d = 5
					if parsedLog[i+1][2] == 1:
						gameState = self.move_stuff(gameState, 2,d, player, Cardstack({}))
						gameState = self.move_stuff(gameState, 4,d, player, Cardstack({}))
						
			#Marking turns, shuffles
			if pred == 1:
				turnBreaks[player].append(i)
				turncount +=1
			elif pred in [31,46]:
				shuffles[player].append(i)

			#let's move some stuff!
			source = 999
			destination = 999

			#General Behavior.
			if len(predData) == 3:
				source = int(predData[1])
				destination = int(predData[2])

			if indent > 0:
				#Exceptions
				if len(indentTree[-2][3].cardList()) > 0:
					activeExceptionsList = [self.exceptions[x] for x in indentTree[-2][3].cardList() if x !=4095]
					activeExceptionsList.append(self.exceptions[0])
					activeExceptions = []
					for i in activeExceptionsList:
						activeExceptions += i
				else:
					activeExceptions = self.exceptions[0]


				for exception in activeExceptions:
					if pred in [x.id for x in exception.target_preds.all()]:
						if indentTree[-2][2] in [x.id for x in exception.root_preds.all()] or \
												exception.root_preds.count() == 0:
							if items.cardList()[0] in [x.id for x in exception.target_cards.all()] or \
														exception.target_cards.count() == 0:
								source = exception.source
								destination = exception.destination
				#Gain to topdeck
				if pred ==12:
					if indentTree[-2][2] in range(2,6):
						#sometimes this bugs out
						if 1 in items:
							items = indentTree[-2][3]

						if items.val == indentTree[-2][3].val:
							source = 5
							destination = 1

			if source != destination:
				if 4095 in items:
					del items.val[4095]
				gameState = self.move_stuff(gameState, source, destination, player, items)

			completeState.append(deepcopy(gameState))

		return [completeState,turnBreaks,shuffles]

	def get_turn_data(self, turnPoints, shufflePoints, decisions):
		allTurns = sorted(reduce(lambda x,y: x+y, turnPoints)+[decisions-1])
		playerCount = len(turnPoints)
		turnOwners = [list(filter(lambda i:x in turnPoints[i],range(playerCount)))[0] for x in allTurns[:-1]]
		shuffleTurns = [[reduce(lambda x,y: x or y, [x in range(allTurns[i],allTurns[i+1]) 
				for x in shufflePoints[player]]) for i in range(len(allTurns)-1)] for player in range(playerCount)]

		return [allTurns, turnOwners, shuffleTurns]

	def get_involved_cards(self, gameStates, allTurns):
		involvedCards = set()
		playerCount = len(gameStates[0][1])

		for t in allTurns:
			theState = gameStates[t]
			combined = reduce(lambda x,y:x+y,[theState[i][0] + theState[i][1] for i in [1,2,4,5,6]])
			involvedCards.update(combined)

		involvedCards = list(involvedCards)
		involvedCards.sort()
		return involvedCards

	def digest_and_sort(self, cardStack, overallClass):
		t = []
		for card in cardStack:
			t.append([card,overallClass,cardStack[card]])

		t.sort()
		return t

	def find_turn_decks(self, gameStates, allTurns, turnOwners):
		playerCount = len(gameStates[0][1])
		turnStartDecks = [[] for i in range(playerCount)]

		for p in range(playerCount):
			for t in allTurns:
				theState = gameStates[t]
				combined = reduce(lambda x,y:x+y,[theState[i][p] for i in [1,2,4,5,6]])
				turnStartDecks[p].append(self.digest_and_sort(combined,''))
		return turnStartDecks

	def find_gained_cards(self, gameStates, allTurns, turnOwners):
		playerCount = len(gameStates[0][1])
		playerDecks = [[] for i in range(playerCount)]

		for p in range(playerCount):
			for i in range(len(allTurns)-1):
				colcards = []
				theState = gameStates[allTurns[i]]
				gainedCards = Cardstack({})
				trashedCards = Cardstack({})

				turnStart = reduce(lambda x,y:x+y,[theState[i][p] for i in [1,2,4,5,6]])
				lastStep = turnStart

				for turn in range(allTurns[i],allTurns[i+1]+1):

					theState = gameStates[turn]
					deck = theState[1][p]
					hand = theState[2][p]
					combined = reduce(lambda x,y:x+y,[theState[i][p] for i in [1,2,4,5,6]])

					gainedCards += combined - lastStep
					trashedCards += lastStep - combined

					lastStep = combined

				diff = trashedCards - turnStart
				colcards+= self.digest_and_sort(trashedCards,'redoutline faded')
				colcards+= self.digest_and_sort(diff,'redoutline')
				colcards+= self.digest_and_sort(gainedCards-diff,'')

				playerDecks[p].append(colcards)

		return playerDecks

	def find_full(self, gameStates, allTurns, turnOwners):
		playerCount = len(gameStates[0][1])
		playerDecks = [[] for i in range(playerCount)]

		for p in range(playerCount):
			for i in range(len(allTurns)-1):
				colcards = []
				theState = gameStates[allTurns[i]]
				seenCards = []
				startDisc = theState[5][p]
				startDeck = theState[1][p]
				startSeen = reduce(lambda x,y:x+y,[theState[i][p] for i in [2,4,6]])
				lastSeen = startSeen
				seenStack = lastSeen
				for card in lastSeen:
					for j in range(lastSeen[card]):
						seenCards.append([card,''])

				for turn in range(allTurns[i],allTurns[i+1]-1):
					theState = gameStates[turn]
					seen = reduce(lambda x,y:x+y,[theState[i][p] for i in [2,4,6]])
					seenDiff = seen - lastSeen
					for card in seenDiff:
						for j in range(seenDiff[card]):
							seenCards.append([card,''])

					seenStack += seenDiff
					lastSeen = seen

				endDeck = startDeck - (seenStack - startSeen)
				endDisc = startDisc - (seenStack - startSeen - startDeck)

				colcards+=self.digest_and_sort(endDisc,'faded')
				colcards+=seenCards
				colcards+=self.digest_and_sort(endDeck,'faded')

				playerDecks[p].append(colcards)

		return playerDecks

	def elaborate_cards(self, cardlist):
		phrases = []
		for item in cardlist:
			if item != 4095:
				rightC = self.cards[item]
				thisPhrase = ''

				if cardlist[item] == 1:
					thisPhrase = rightC[2]
				elif cardlist[item] == 0:
					thisPhrase = rightC[0]
				else:
					thisPhrase = '{} {}'.format(cardlist[item],rightC[1])

				thisPhrase = self.makeDiv('story-color', thisPhrase, 
					{'card': item,
					 'style':'background:#{}; outline-color:#{};'.format(
					 	self.cardcolors[item], self.bordercolors[item])
					})
				phrases.append(thisPhrase)

		if len(phrases)>1:
			phrases[-1] = 'and ' + phrases[-1]

		return ', '.join(phrases)

	def elaborate_story(self, players, gamelog):
		lines = []
		for entry in gamelog:
			if 4095 in entry[3]:
				argumentsSplit = entry[3][4095].split('/')
			else:
				argumentsSplit = []

			entryString = self.preds[entry[2]][0]
			entryString = re.sub(r'\^?\(\?P<player>\.\*\)',players[entry[0]-1],entryString)
			entryString = entryString.replace('^(?P<player>Game)','Game')

			elab = self.elaborate_cards(entry[3])
			if elab != '':
				entryString = re.sub(r'\(\?P<cards>(\.\*|\\d\+)\)',elab,entryString)
			elif len(argumentsSplit) > 0:
				if re.search(r'\(\?P<cards>(\.\*|\\d\+)\)',entryString) != None:
					entryString = re.sub(r'\(\?P<cards>(\.\*|\\d\+)\)',argumentsSplit.pop(0),entryString)

			entryString = reduce(lambda x,y: re.sub(r'\(\.\*\)',y,x),argumentsSplit,entryString)

			entryString = re.sub(r'\\([\.\(\)])',r'\1',entryString)
			entryString = re.sub('\^|\$|\*','',entryString)
			lines.append(entryString)

		indents = [x[1] for x in gamelog]
		owners = [x[0] for x in gamelog]
		return [lines,indents,owners]

	def makeDiv(self, classes,innerHTML='',otherTags={}):
		otherTagString = ' '.join(['{} = \'{}\''.format(x,otherTags[x]) for x in otherTags])
		if innerHTML != '':
			innerHTML = '{}\n'.format(innerHTML.replace('\n', '\n\t'))
		return '\n<div class = \'{}\' {}>{}</div>'.format(classes,otherTagString,innerHTML)

	def render_graph_bg_row(self, turnOwners, stripe, side):

		t = [self.makeDiv('col' + (' active' if turnOwners[i] == side else ''),
			self.makeDiv('leftstripe active' if stripe[i-1] else 'leftstripe')) for i in range(len(turnOwners))]
		return ''.join(t)

	def render_graph_axis(self, turnOwners):
		axisLabelsString = ''
		t = 0
		for turnO in turnOwners:
			if turnO == 0:
				t += 1
			axisLabelsString += self.makeDiv('axislabel',str(t)+'<br>'+'abcdef'[turnO])

		axisLabelsString += self.makeDiv('axislabel','e<br>n<br>d')

		return axisLabelsString

	def render_graph_row(self, cardList, involvedCards, side):
		innerText = ''
		outString = ''
		colHeight = [0 for i in range(len(cardList))]
		direction = ['bottom','top'][side]
		layerStrings = ['' for i in involvedCards]

		for index in range(len(cardList)):
			for card in cardList[index]:
				layerIndex = involvedCards.index(card[0])
				if len(card) ==2:
					length = 1
				else:
					length = card[2]

				for j in range(length):
					cardString = self.makeDiv('box-inner ', otherTags={
											 'style':'background: #{}'.format(self.cardcolors[card[0]])
											 })

					rightHeight = 1.75*(colHeight[index]) + 0.5*(colHeight[index]//5)
					order = colHeight[index]

					cardString = self.makeDiv('box '+card[1],  cardString,
											 {
											 'style':'background:#{}; {}:{}vh; left:{}vh;'.format(
											 	self.bordercolors[card[0]],direction,rightHeight,2.5*(index)+0.4),
											 'card':card[0],
											 'cost':self.costs[index],
											 'side':2*(0.5-side),
											 'ycoord':order,
											 'currenty':order,
											 'xcoord':index
											 }
											)

					colHeight[index] += 1
					layerStrings[layerIndex] += cardString
		layerStrings = [self.makeDiv('graph-layer card'+str(involvedCards[i]),layerStrings[i]) for 
							i in range(len(layerStrings))]
		outString = ''.join(layerStrings)
		return outString

	def render_legend(self, involvedCards):
		legendString = ''
		for card in involvedCards:
			legendString += self.makeDiv(	'legendbox',
									self.makeDiv('inner-color',self.cardPrimaries[card],
										{'style': 'background: #{};'.format(self.cardcolors[card])
										}),
											{'style':
											'background: #{};'.format(self.bordercolors[card]),
											'card':card})
		return legendString

	def render_story_main(self, story, turnBreaks):
		paddings = [(x+2)*2 for x in story[1]]
		highlights = ['story-line' + (' alternate' if x == 1 else '') for x in story[2]]
		turns = [turnBreaks.index(x) if x in turnBreaks else -1 for x in range(len(story[0]))]
		return ''.join([self.makeDiv(highlights[i],story[0][i],
						{'style':'padding-left:{}%'.format(paddings[i]),
						 'turn':turns[i]}) for i in range(len(story[0]))])

	def render_story_sidebar(self, turnOwners, turnBreaks):
		sidebarstr = ''
		t = 0
		for i in range(len(turnOwners)):
			if turnOwners[i] == 0:
				t += 1
			length = turnBreaks[i+1]-turnBreaks[i]
			sidebarstr += self.makeDiv('story-sidebar-block' if i%2==1 else 'story-sidebar-block alternate',
								  str(t)+'abcdef'[turnOwners[i]],{
								  'style':'flex-grow:{}'.format(length),
								  'turn':i})

		return sidebarstr

	def render_kingdom(self, supply):
		outstrs = ['' for i in range(3)]
		supply = sorted(supply, key = lambda x: (self.costs[x], self.cardPrimaries[x]))
		for card in supply:
			supplytype = self.supplytypes[card]
			if supplytype > -1:
				outstrs[supplytype] += 	self.makeDiv('kingdom-card',
								self.makeDiv('inner-color',self.cardPrimaries[card],
									{'style': 'background: #{};'.format(self.cardcolors[card])
									}),
										{'style':
										'background: #{};'.format(self.bordercolors[card]),
										'card':card})
		return outstrs