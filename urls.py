# -*- coding: utf-8 -*-
from django.urls import path

from . import views

app_name = "woodcutter"
urlpatterns = [
    path("", views.main, name="index"),
    path("input", views.inputFields, name="inputform"),
    path("submit", views.submit, name="submit"),
    path("errorlist", views.logSearch, name="errorlist"),
    path("random", views.random, name="random"),
    path("logsearch", views.logSearch, name="searchPage"),
    path("findlogs", views.find_logs, name="findlogs"),
    path("<int:game_id>/display/", views.display, name="display"),
    path("<int:game_id>/plain/", views.plaintext, name="plain"),
    path("<int:game_id>/detail/", views.detailed, name="detail"),
    path("<int:game_id>/display/<int:logIndex>", views.display),
    path("<int:game_id>/debug/", views.dump, name="dump"),
]
