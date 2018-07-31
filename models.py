from django.db import models


class GameLog(models.Model):
    def __str__(self):
        return str(self.game_id)

    game_id = models.IntegerField(default=0, primary_key=True)

    log = models.CharField(
                    max_length=15000,
                    default='',
                    blank=True)

    supply = models.CharField(
                    max_length=1000,
                    default='',
                    blank=True)

    players = models.CharField(
                    max_length=100,
                    default='',
                    blank=True)

    valid = models.BooleanField(default=True)
