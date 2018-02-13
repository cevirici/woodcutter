from django.db import models

class GameLog(models.Model):
	def __str__(self):
		return str(self.game_id)

	game_id = models.IntegerField(default=0, primary_key = True)

	log = models.CharField(
					max_length=10000,
					default='',
					blank=True)

	supply = models.CharField(
					max_length=500,
					default='',
					blank=True)

class CardData(models.Model):
	def __str__(self):
		return self.single_name+ '({})'.format(str(hex(self.id)))

	id = models.IntegerField(primary_key=True)
	single_name = models.CharField(max_length=30)
	multi_name = models.CharField(max_length=30, blank= True)
	phrase_name = models.CharField(max_length=30, blank = True)
	cost = models.IntegerField()
	color = models.CharField(max_length=8)
	border_color = models.CharField(max_length=8)

	class Meta:
		ordering = ['id']

class PredData(models.Model):
	def __str__(self):
		return str(self.id)+':'+self.regex

	id = models.IntegerField(primary_key=True)
	regex = models.CharField(max_length=150)
	source = models.IntegerField(blank=True)
	destination = models.IntegerField(blank=True)

	class Meta:
		ordering = ['id']

class ExceptionData(models.Model):
	def __str__(self):
		return 'Doing {} with {} from {} to {}'.format(
									','.join([str(x) for x in self.target_preds.all()]),
									self.root_card,
									str(self.source),
									str(self.destination),
									)

	root_card = models.ForeignKey('CardData', on_delete=models.CASCADE, verbose_name = 'root Card', related_name = 'exceptions')
	root_preds = models.ManyToManyField('PredData', verbose_name = 'root Preds', related_name = '+', blank=True)
	target_cards = models.ManyToManyField('CardData', verbose_name = 'target Cards', blank = True)
	target_preds = models.ManyToManyField('PredData', verbose_name = 'target Preds', related_name = '+', blank=True)
	source = models.IntegerField(blank=True)
	destination = models.IntegerField(blank=True)

