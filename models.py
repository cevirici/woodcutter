from django.db import models
from django.urls import reverse


class GameLog(models.Model):
    def __str__(self):
        return str(self.game_id)

    def get_absolute_url(self, obj):
        url = reverse('plain', kwargs={'game_id': obj.game_id})
        return url

    game_id = models.IntegerField(default=0, primary_key=True)

    log = models.CharField(max_length=20000,
                           default='',
                           blank=True)

    supply = models.CharField(max_length=1000,
                              default='',
                              blank=True)

    players = models.CharField(max_length=100,
                               default='',
                               blank=True)

    valid = models.BooleanField(default=True)
