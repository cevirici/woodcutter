# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import GameLog
from django.urls import reverse
from django.utils.safestring import mark_safe


def getNames(log):
    return " vs. ".join(log.players.split("~"))


@mark_safe
def get_urls(obj):
    urlstring = "<a href={}> Display </a> \
<a href={}> Detail </a> <a href={}> Plain </a>"
    return urlstring.format(
        reverse("woodcutter:display", args=(obj.game_id,)),
        reverse("woodcutter:detail", args=(obj.game_id,)),
        reverse("woodcutter:plain", args=(obj.game_id,)),
    )


class logAdmin(admin.ModelAdmin):
    list_display = ("valid", "game_id", getNames, get_urls)


admin.site.register(GameLog, logAdmin)
