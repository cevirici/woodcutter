import copy

from .classes import *
from .standards import *

def unpack(logstring, supplystring):
	t = logstring.split('~')
	g = []
	for c in t:
		player = int(c[0:1], 16)-1
		indent = int(c[1:2], 16)
		pred = int(c[2:4], 16)
		cardString = c[4:]

		if len(cardString)>0:
			cards = [x.split(':') for x in cardString.split('|')]
			for card in cards:
				if int(card[1],16) != ARGUMENT_CARD:
					card[0] = int(card[0])
			stack = Cardstack({int(x[1],16):x[0] for x in cards})
		else:
			stack = Cardstack({})

		g.append(ParsedLine(player,indent,pred,stack))

	t = supplystring.split('~')
	s = Cardstack({})
	for c in t:
		card = int(c[0:3],16)
		amount = int(c[3:5])
		s+=Cardstack({card:amount})

	return [g,s]

class gameState:
	def __init__(self):
		self.SUPPLY = [Cardstack({})]
		self.DECKS = [Cardstack({}), Cardstack({})]
		self.HANDS = [Cardstack({}), Cardstack({})]
		self.INPLAYS = [Cardstack({}), Cardstack({})]
		self.DISCARDS = [Cardstack({}), Cardstack({})]
		self.OTHERS = [Cardstack({}),Cardstack({})]
		self.TRASH = [Cardstack({})]
		self.coins = [0,0]
		self.coinsLower = [0,0]

	def __str__(self):
		outstr = ''
		for zone in ['SUPPLY','DECKS','HANDS','INPLAYS','DISCARDS','OTHERS','TRASH']:
			outstr +='\n    '+zone
			for part in getattr(self, zone):
				outstr += '\n    '+str(part)

		outstr += '\n------\n'
		return outstr

	def move(self, player, src, dest, items):
		itemsNoArgs = deepcopy(items)
		if ARGUMENT_CARD in items:
			del itemsNoArgs.val[ARGUMENT_CARD]

		getattr(self, src)[min(len(getattr(self, src))-1, player)] -= itemsNoArgs
		getattr(self, dest)[min(len(getattr(self, dest))-1, player)] += itemsNoArgs

	def add(self, player, dest, items):
		getattr(self, dest)[min(len(getattr(self, dest))-1, player)] += items

	def crunch(self, zonelist, playerlist):
		outlist = Cardstack({})
		for zone in zonelist:
			if len(getattr(self, zone)) > 1:
				for player in playerlist:
					outlist += getattr(self, zone)[player]
			else:
				outlist += getattr(self, zone)[0]

		return outlist


def parse_game(parsedLog):
	moveTree = []
	currentTurn = []
	for i in range(len(parsedLog)):
		currentMove = parsedLog[i]
		if currentMove.pred == NEWTURN_PRED:
			moveTree.append(currentTurn)
			currentTurn = [currentMove]
		else:
			if currentMove.pred == currentMove.pred == GAMESTART_PRED:
				currentTurn = [currentMove]
			else:
				pointer = currentTurn
				for j in range(currentMove.indent):
					pointer = pointer[-1]

				pointer.append([currentMove])

	moveTree.append(currentTurn)

	return moveTree

def get_decision_state(moveTree, supply):
	startState = gameState()
	startState.add(0, 'SUPPLY', supply)
	gameStates = [startState]

	for turn in moveTree:
		turnExceptions = []
		def parse_chunk(chunk, exceptions, turnExceptions, persistents):
			subexceptions = copy.copy(exceptions)
			gameStates.append(deepcopy(gameStates[-1]))

			passedExceptions = [exception for exception in exceptions + persistents 
			                    if exception.condition(chunk) == True]
			#One-time
			passedTurnExceptions = [exception for exception in turnExceptions if exception.condition(chunk) == True]

			if passedExceptions + passedTurnExceptions:
				for exception in passedExceptions + passedTurnExceptions:
					exception.action(chunk, gameStates, subexceptions, turnExceptions, persistents)
					
				for exception in passedTurnExceptions:
					turnExceptions.remove(exception)
			else:
				standardPreds[chunk[0].pred].action(chunk, gameStates, subexceptions, turnExceptions, persistents)

				for card in chunk[0].items:
					if card != ARGUMENT_CARD:
						for i in range(chunk[0].items[card]):
							standardCards[card].action(chunk, gameStates, subexceptions, turnExceptions, persistents)

			for subchunk in chunk[1:]:
				parse_chunk(subchunk, subexceptions, turnExceptions, persistents)

		parse_chunk(turn, [], turnExceptions, standardPersistents)

	return gameStates

def get_turn_points(moveTree):
	#Position of last decision in each turn, including the pregame turn
	def get_chunk_length(chunk):
		return sum([get_chunk_length(x) for x in chunk[1:]]) + 1
	lens = [get_chunk_length(chunk) for chunk in moveTree]
	return [sum(lens[:i+1])-1 for i in range(len(lens))]

def get_cleanup_points(moveTree):
	#Look for the first nonindented shuffle/draw
	def find_cleanup_chunk(chunk):
		if chunk[0].indent == 0 and chunk[0].pred in CLEANUP_PREDS:
			return 1
		else:
			t = -1
			for subchunk in chunk[1:]:
				if find_cleanup_chunk(subchunk) < 0:
					t += find_cleanup_chunk(subchunk)
				else:
					t = -t + find_cleanup_chunk(subchunk)
					return t
			return t

	return [abs(find_cleanup_chunk(chunk)) for chunk in moveTree]

def get_turn_owners(moveTree):
	return [chunk[0].player for chunk in moveTree]

def get_shuffled_turns(moveTree):
	def had_shuffled(player, chunk):
		if chunk[0].pred == SHUFFLE_PRED and chunk[0].player == player:
			return True
		else:
			if [x for x in chunk[1:] if had_shuffled(player, x)]:
				return True
			else:
				return False

	return [[had_shuffled(p,x) for x in moveTree] for p in range(2)]

def get_involved_cards(gameStates):
	involvedCards = set()

	for state in gameStates:
		involvedCards.update(state.crunch(['DECKS','HANDS','INPLAYS','DISCARDS','OTHERS','TRASH'],[0,1]))

	involvedCards = list(involvedCards)
	involvedCards.sort()
	return involvedCards

def find_turn_decks(turnPoints, gameStates):
	turnDecks = [[] for i in range(2)]
	for point in turnPoints:
		for p in range(2):
			turnDecks[p].append(gameStates[point+1].crunch(['DECKS','HANDS','INPLAYS','DISCARDS','OTHERS'],[p]))

	return [turnDecks]

def find_gained_cards(turnPoints, gameStates):
	netGains = [[Cardstack({})] for i in range(2)]
	netTrashes = [[Cardstack({})] for i in range(2)]
	stepGains = [[Cardstack({})] for i in range(2)]

	for index in range(len(turnPoints) - 1):
		for p in range(2):
			startDeck = gameStates[turnPoints[index] + 1].crunch(
			            ['DECKS','HANDS','INPLAYS','DISCARDS','OTHERS'],[p])
			endDeck = gameStates[turnPoints[index + 1] + 1].crunch(
			          ['DECKS','HANDS','INPLAYS','DISCARDS','OTHERS'],[p])
			netGain = endDeck - startDeck
			netTrash = startDeck - endDeck

			stepGain = Cardstack({})

			for i in [turnPoints[index] + 1, turnPoints[index + 1]]:
				stepGain += gameStates[i+1].crunch(['DECKS','HANDS','INPLAYS','DISCARDS','OTHERS'],[p]
				            ) - gameStates[i].crunch(['DECKS','HANDS','INPLAYS','DISCARDS','OTHERS'],[p])

			stepGain = stepGain - netGain
			netGains[p].append(netGain)
			netTrashes[p].append(netTrash)
			stepGains[p].append(stepGain)

	return [netTrashes, stepGains, netGains]

def find_shuffle_progress(turnPoints, cleanupPoints, gameStates):
	#subset?
	turnPointsPlus = [-1] + turnPoints

	decks = [[] for i in range(2)]
	startingHands = [[] for i in range(2)]
	actives = [[] for i in range(2)]
	discards = [[] for i in range(2)]

	for index in range(len(turnPoints)):
		for p in range(2):
			endDeck = gameStates[cleanupPoints[index]].crunch(
			          ['DECKS','HANDS','INPLAYS','DISCARDS','OTHERS'],[p])
			discard = gameStates[cleanupPoints[index]].crunch(['DISCARDS'],[p])

			active = gameStates[turnPointsPlus[index] + 1].crunch(['HANDS','INPLAYS','OTHERS'], [p])

			for i in range(turnPointsPlus[index] + 1 , cleanupPoints[index]):
				active += gameStates[i + 1].crunch(['HANDS','INPLAYS','OTHERS'],[p] 
				          ) - gameStates[i].crunch(['HANDS','INPLAYS','OTHERS'],[p])

	        #Making sure active is a subset of the full deck
			diff = active - endDeck
			active = active - diff

			remainder = endDeck - active
			deck = remainder - discard
			discard = remainder - deck

			decks[p].append(deck)
			actives[p].append(active)
			discards[p].append(discard)

	return [discards, actives, decks]