from copy import deepcopy

class Cardstack:
	def __init__(self,cards):
		self.val = cards

	def __add__(self,other):
		t = deepcopy(self.val)
		for c in other:
			if c != 4095:
				if c in t:
					t[c] += other.val[c]
				else:
					t[c] = other.val[c]
		return Cardstack(t)

	def __sub__(self,other):
		t = deepcopy(self.val)
		for c in other:
			if c != 4095:
				if c in t:
					t[c] -= other.val[c]

		t = {c:v for c,v in t.items() if v > 0}
		return Cardstack(t)


	def __iter__(self):
		for card in list(self.val):
			yield card

	def insert(self, item, number):
		if item != 4095:
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