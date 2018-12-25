from django.contrib import admin
from .models import GameLog


def getNames(log):
    return ' vs. '.join(log.players.split('~'))


class logAdmin(admin.ModelAdmin):
    view_on_site = True
    list_display = ('valid', 'game_id', getNames)


admin.site.register(GameLog, logAdmin)
