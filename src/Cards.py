# -*- coding: utf-8 -*-
from .Enums import *


def getKeyCard(card):
    keyCards = {
        "Knights": "Knights",
        "Sir Bailey": "Knights",
        "Sir Destry": "Knights",
        "Sir Martin": "Knights",
        "Sir Michael": "Knights",
        "Sir Vander": "Knights",
        "Dame Anna": "Knights",
        "Dame Josephine": "Knights",
        "Dame Molly": "Knights",
        "Dame Natalie": "Knights",
        "Dame Sylvia": "Knights",
        "Ruin Pile": "Ruin Pile",
        "Abandoned Mine": "Ruin Pile",
        "Ruined Library": "Ruin Pile",
        "Ruined Market": "Ruin Pile",
        "Ruined Village": "Ruin Pile",
        "Survivors": "Ruin Pile",
        "Castles": "Castles",
        "Humble Castle": "Castles",
        "Crumbling Castle": "Castles",
        "Small Castle": "Castles",
        "Haunted Castle": "Castles",
        "Opulent Castle": "Castles",
        "Sprawling Castle": "Castles",
        "Grand Castle": "Castles",
        "Kings Castle": "Castles",
        "Encampment": "Encampment",
        "Plunder": "Encampment",
        "Patrician": "Patrician",
        "Emporium": "Patrician",
        "Settlers": "Settlers",
        "Bustling Village": "Settlers",
        "Catapult": "Catapult",
        "Rocks": "Catapult",
        "Gladiator": "Gladiator",
        "Fortune": "Gladiator",
        "Sauna": "Sauna",
        "Avanto": "Sauna",
        "Zombie Apprentice": "Zombie Apprentice",
        "Zombie Mason": "Zombie Apprentice",
        "Zombie Spy": "Zombie Apprentice",
    }
    if card in keyCards:
        return keyCards[card]
    else:
        return card


def getPileCards(card):
    piles = {
        "Knights": [
            "Knights",
            "Sir Bailey",
            "Sir Destry",
            "Sir Martin",
            "Sir Michael",
            "Sir Vander",
            "Dame Anna",
            "Dame Josephine",
            "Dame Molly",
            "Dame Natalie",
            "Dame Sylvia",
        ],
        "Ruin Pile": [
            "Ruin Pile",
            "Abandoned Mine",
            "Ruined Library",
            "Ruined Market",
            "Ruined Village",
            "Survivors",
        ],
        "Castles": [
            "Castles",
            "Humble Castle",
            "Crumbling Castle",
            "Small Castle",
            "Haunted Castle",
            "Opulent Castle",
            "Sprawling Castle",
            "Grand Castle",
            "Kings Castle",
        ],
        "Encampment": ["Encampment", "Plunder"],
        "Patrician": ["Patrician", "Emporium"],
        "Settlers": ["Settlers", "Bustling Village"],
        "Catapult": ["Catapult", "Rocks"],
        "Gladiator": ["Gladiator", "Fortune"],
        "Sauna": ["Sauna", "Avanto"],
        "Zombie Apprentice": ["Zombie Apprentice", "Zombie Mason", "Zombie Spy"],
    }
    keyCard = getKeyCard(card)
    if keyCard in piles:
        return piles[keyCard]
    else:
        return [card]


def getInitialZone(card):
    if getKeyCard(card) == "Zombie Apprentice":
        return NeutralZones.TRASH
    else:
        return NeutralZones.SUPPLY


def isOrderedPile(card):
    orderedKeyCards = [
        "Castles",
        "Encampment",
        "Patrician",
        "Settlers",
        "Catapult",
        "Gladiator",
        "Sauna",
    ]
    return getKeyCard(card) in orderedKeyCards


def isAction(card):
    return False


def isTreasure(card):
    return True
