import re
from functools import reduce
from ceviri_net.settings import BASE_DIR
from .cardstack import Cardstack


class Parser:
	def __init__(self,preds,cards):
		self.preds = []
		for pred in preds:
			self.preds.append([pred.regex,pred.source,pred.destination])

		self.cards = []
		for card in cards:
			self.cards.append([card.single_name,card.multi_name,card.phrase_name])


	def get_indent(self,line):
		t = re.search('padding-left:(.*?)em;',line).group(1)
		return int(float(t)//1.5)

	def get_normalized_name(self,name):
		for i in range(len(self.cards)):
			if name in self.cards[i]:
				return i

		print('Unknown card {} found'.format(name))
		return 0

	def card_list_splitter(self,cardlist):
		r = re.split(', | and ', cardlist)
		a = Cardstack({})

		for item in r:
			item = item.split(' ',1)
			if len(item) == 2:
				if re.match('^\d+$|^an?$',item[0]) != None:
					if item[0] in ['a','an']:
						item[0] = 1

					item[0] = int(item[0])
				else:
					item[1] = ' '.join(item)
					item[0] = 0

				item[1] = self.get_normalized_name(item[1])

				a.insert(item[1],item[0])
			else:
				if re.match('^\d+$',item[0]) != None:
					item[0] = int(item[0])
				a.insert(4095,item[0])

		return a


	def get_arguments(self,line):
		indent = self.get_indent(line)
		line = line.strip()
		line = re.sub('<.*?>|&bull;|&sdot;','',line)

		for x in range(len(self.preds)):
			if re.match(self.preds[x][0],line) != None:
				pred = x
				break

		m = re.match(self.preds[pred][0], line)
		player = -1
		lowlim = 3
		try:
			player = m.group('player')
		except:
			lowlim -= 1

		cards = Cardstack({})
		try:
			c_raw = m.group('cards')
			cards = self.card_list_splitter(c_raw)
		except:
			lowlim -= 1

		for i in range(lowlim,len(m.groups())+1):
			cards.insert(4095,m.group(i))

		return [player, indent, pred, cards]

	def translate_file(self,inString):
		f = inString.split('~')
		a = []
		player_list = []
		backup_player = ''
		for line in f:
			t = self.get_arguments(line)

			#Player handling - special exception for 'Turn n' pred, because that uses long names.
			#gaaah some preds have no player.
			if t[0] == -1:
				t[0] = backup_player
			else:
				if t[2] != 1:
					if t[0] not in player_list:
						player_list.append(t[0])
				else:
					match_names = list(filter(lambda x: re.match('^'+x,t[0])!=None,player_list))
					t[0] = list(filter(lambda x: len(x) == max([len(y) for y in match_names]),match_names))[0]

			backup_player = t[0]
			t[0] = player_list.index(t[0])
			a.append(t)
		return [a,len(player_list)]

	def parse_supply(self,inString):
		f = inString.split('~')
		cards = []

		for line in f:
			r = line.strip().rsplit("-",1)
			card = self.get_normalized_name(r[0])
			quant = '{:0>2}'.format(r[1])
			cards.append('{:0>3}'.format(hex(card)[2:])+quant)

		outstr = '~'.join(cards)
		return outstr

	def combined_parse(self,inStrings):
		raws = [self.translate_file(x) for x in inStrings]
		a = []
		logs = [x[0] for x in raws]
		gameNum = int(logs[0][0][3][4095].split('/')[0])

		for i in range(len(logs[0])):
			t = [x[i] for x in logs]
			combined = t[0][:]

			for s_t in t:
				if s_t[0:3] != combined[0:3]:
					self.files_dont_match('||'.join([str(s_t[0:3]),str(combined[0:3])]))
					break

				if 1 not in s_t[3]:
					combined[3] = s_t[3]

			combined[0] = hex(combined[0])[2:]
			combined[1] = hex(combined[1])[2:]
			combined[2] = '{:0>2}'.format(hex(combined[2])[2:])
			a.append(''.join([str(x) for x in combined]))

		outstr = '~'.join(a)
		return [outstr,gameNum]

	def files_dont_match(self,line):
		print('uh oh!{}'.format(line))


