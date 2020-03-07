from .Enums import *
from django.conf import settings
import os


class InvalidMove(Exception):
    pass


class LogMismatch(Exception):
    pass


def getPred(logLine):
    return int(logLine.split('|')[1])


def getOwner(logLine):
    return int(logLine.split('|')[2])


def getItems(logLine):
    itemString = logLine.split('|')[3]
    items = []
    for item in itemString.split('+'):
        index, freq = [int(x) for x in item.split(':')]
        items.extend([CardNames(index) for i in range(freq)])
    return items


def getInfo(version):
    cardPath = 'woodcutter/data/cardv3.txt'
    cardF = open(os.path.join(settings.STATIC_ROOT, cardPath), 'r')
    cardNames = [line for line in cardF]

    if version == 2:
        predPath = 'woodcutter/data/predv2.txt'
    else:
        predPath = 'woodcutter/data/predv3.txt'
    predF = open(os.path.join(settings.STATIC_ROOT, predPath), 'r')
    predNames = [line for line in predF]
    return (cardNames, predNames)
