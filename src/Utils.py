# -*- coding: utf-8 -*-
from .Enums import *
from django.conf import settings
import os

PLAYER_COUNT = 2


class InvalidMove(Exception):
    pass


class LogMismatch(Exception):
    pass


def getPred(logLine):
    return int(logLine.split("|")[1])


def getOwner(logLine):
    return int(logLine.split("|")[2])


def getItems(logLine):
    itemString = logLine.split("|")[3]
    items = []
    for item in itemString.split("+"):
        index, freq = [int(x) for x in item.split(":")]
        items.extend([CardNames(index) for i in range(freq)])
    return items


def getInfo(version):
    if version in [0, 1, 9]:
        cardPath = "woodcutter/data/cardv1.txt"
    else:
        cardPath = "woodcutter/data/cardv3.txt"
    cardF = open(os.path.join(settings.STATIC_ROOT, cardPath), "r")
    cardNames = [line.strip() for line in cardF]

    if version == 0:
        predPath = "woodcutter/data/predv0.txt"
    elif version == 1:
        predPath = "woodcutter/data/predv1.txt"
    elif version == 2:
        predPath = "woodcutter/data/predv2.txt"
    else:
        predPath = "woodcutter/data/predv3.txt"
    predF = open(os.path.join(settings.STATIC_ROOT, predPath), "r")
    predNames = [line.strip() for line in predF]
    return (cardNames, predNames)
