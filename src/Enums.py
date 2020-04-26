# -*- coding: utf-8 -*-
from enum import Enum


class Actions(Enum):
    PLAY = 0
    DISCARD = 1
    TRASH = 2
    REACT = 3
    GAIN = 4
    BUY = 5
    REVEAL = 6


class TurnTypes(Enum):
    PREGAME = 0
    NORMAL = 1
    MISSION = 2
    POSSESSION = 3
    DONATE = 4


class PlayerZones(Enum):
    DECK = 0
    HAND = 1
    PLAY = 2
    DISCARD = 3
    SET_ASIDE = 4
    NATIVE_VILLAGE = 5
    TAVERN = 6
    POSSESSED = 7


class NeutralZones(Enum):
    SUPPLY = 0
    NON_SUPPLY = 1
    TRASH = 2
    BOON_DISCARD = 3
    HEX_DISCARD = 4
    BLACK_MARKET = 5


class Phases(Enum):
    START_OF_TURN = 0
    ACTION = 1
    TREASURE_PLAYING = 2
    BUY = 3
    NIGHT = 4
    CLEANUP = 5
    PREGAME = 6


class FlagTypes(Enum):
    START_OF_TURN = 0
    CLEANUP = 1
    BUY = 2
    GAIN = 3


class Types(Enum):
    ACTION = 0
    NIGHT = 1
    TREASURE = 2
    ATTACK = 3
    CURSE = 4
    DURATION = 5
    EVENT = 6
    GATHERING = 7
    KNIGHT = 8
    LANDMARK = 9
    LOOTER = 10
    RUINS = 11
    TRAVELLER = 12
    PRIZE = 13
    RESERVE = 14
    VICTORY = 15
    REACTION = 16
    SHELTER = 17
    CASTLE = 18
    FATE = 19
    DOOM = 20
    HEIRLOOM = 21
    SPIRIT = 22
    ZOMBIE = 23
    BOON = 24
    HEX = 25
    STATE = 26
    ARTIFACT = 27
    PROJECT = 28
    COMMAND = 29
    WAY = 30


class argTypes(Enum):
    NUMBER = 0
    CARD = 1
