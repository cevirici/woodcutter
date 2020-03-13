# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from django.conf import settings
from .Card import *
from .Pred import *

Cards = {}
CardList = []
Preds = {}
PredList = []


def empty(i, blockLengths, moves, state):
    return {}


def staticWorth(val):
    def out_function(gS, player):
        return val

    return out_function


cardFile = open(os.path.join(settings.STATIC_ROOT, "woodcutter/data/carddata.txt"), "r")
for line in cardFile:
    t = line.strip().split(",")
    index = int(t[0], 16)
    t_ptr = *t
    c = Card(index, t_ptr[1:9], empty)
    if len(t) > 9:
        c.worth = staticWorth(int(t[9]))

    Cards[t[1].upper()] = c
    CardList.append(c)

cardOrder = {CardList[i].simple_name.upper(): i for i in range(len(CardList))}


def supplyOrder(card):
    supplyCards = [
        "COLONY",
        "PLATINUM",
        "PROVINCE",
        "GOLD",
        "DUCHY",
        "SILVER",
        "ESTATE",
        "COPPER",
        "CURSE",
    ]
    if card in supplyCards:
        return supplyCards.index(card)
    else:
        return cardOrder[card] + len(supplyCards)


CardList.sort(key=lambda c: c.index)
cardFile.close()

predFile = open(os.path.join(settings.STATIC_ROOT, "woodcutter/data/preddata.txt"), "r")
for line in predFile:
    t = line.strip().split("~")
    p = Pred(int(t[0], 16), t[1], empty, t[2])
    Preds[t[2]] = p
    PredList.append(p)

predParseOrder = deepcopy(PredList)
PredList.sort(key=lambda p: p.index)

predFile.close()
