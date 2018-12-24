import os
from django.conf import settings

CARD_URLS_PATH = 'woodcutter/card_images/imageurls.txt'

cardUrls = {}
f = open(os.path.join(settings.STATIC_ROOT, CARD_URLS_PATH))
for line in f:
    raw = line.strip().split(':')
    raw[1] = 'woodcutter/card_images/{}'.format(raw[1][raw[1].rfind('/') + 1:])
    cardUrls[raw[0]] = raw[1]


class Card:
    def __init__(self, index, simple_name, multi_name, phrase_name,
                 cost, supply_type, border_color, card_color,
                 types, action, worth=lambda x, y: 0):

        self.index = index
        self.simple_name = simple_name
        self.multi_name = multi_name
        self.phrase_name = phrase_name
        self.names = [self.simple_name, self.multi_name, self.phrase_name]
        self.cost = cost
        self.supply_type = supply_type
        self.action = action
        self.border_color = border_color
        self.card_color = card_color
        self.types = types
        self.worth = worth

        if self.simple_name in cardUrls:
            self.cardurl = cardUrls[self.simple_name]
        else:
            self.cardurl = cardUrls['card']

    def __repr__(self):
        return '{:0>3}'.format(hex(self.index)[2:])

    def __str__(self):
        return self.simple_name.upper()

    def __hash__(self):
        return self.index

    def __eq__(self, other):
        if type(other) == str:
            return self.simple_name == other
        else:
            return self.index == other.index
