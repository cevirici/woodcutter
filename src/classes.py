from copy import deepcopy
from .standards import *

class Card:
	def __init__(self, simple_name, multi_name, phrase_name,
				 cost, supply_type, border_color, card_color, action):

		self.simple_name = simple_name
		self.multi_name = multi_name
		self.phrase_name = phrase_name
		self.cost = cost
		self.supply_type = supply_type
		self.action = action
		self.border_color = border_color
		self.card_color = card_color

	def names(self):
		return [self.simple_name, self.multi_name, self.phrase_name]

	def action(self, pred):
		self.action(pred)

class Exception:
	def __init__(self, condition, action, name='Exception'):
		self.condition = condition
		self.action = action
		self.name = name

	def __repr__(self):
		return self.name

class Pred:
	def __init__(self, regex, action, name):
		self.regex = regex
		self.action = action
		self.name = name

class ParsedLine:
	def __init__(self, player, indent, pred, items):
		self.player = player
		self.indent = indent
		self.pred = pred
		self.items = items

	def __str__(self):
		return str(self.player)+str(self.indent)+str(self.pred)+str(self.items)

	def __repr__(self):
		return str(self.player)+str(self.indent)+str(self.pred)+str(self.items)

class Cardstack:
	def __init__(self,cards):
		self.val = cards

	def __add__(self,other):
		t = deepcopy(self.val)
		for c in other:
			if c != ARGUMENT_CARD:
				if c in t:
					t[c] += other.val[c]
				else:
					t[c] = other.val[c]
		return Cardstack(t)

	def __sub__(self,other):
		t = deepcopy(self.val)
		for c in other:
			if c != ARGUMENT_CARD:
				if c in t:
					t[c] -= other.val[c]

		t = {c:v for c,v in t.items() if v > 0}
		return Cardstack(t)


	def __iter__(self):
		for card in list(self.val):
			yield card

	def insert(self, item, number):
		if item != ARGUMENT_CARD:
			if item in self.val:
				self.val[item] += number
			else:
				self.val[item] = number
		else:
			if item in self.val:
				self.val[item] += '/'+str(number)
			else:
				self.val[item] = str(number)


	def __str__(self):
		t = ['{}:{}'.format(self.val[i],hex(i)[2:]) for i in self.val]
		outstr = '|'.join(t)
		return outstr

	def __repr__(self):
		t = ['{}:{}'.format(self.val[i],hex(i)[2:]) for i in self.val]
		outstr = '|'.join(t)
		return outstr

	def __getitem__(self,item):
		return self.val[item]

	def cardList(self):
		return list(self.val)

	def getval(self):
		return self.val