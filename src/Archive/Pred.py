# -*- coding: utf-8 -*-
class Pred:
    def __init__(self, index, regex, action, name):
        self.index = index
        self.regex = regex
        self.action = action
        self.name = name

    def __repr__(self):
        return "{:0>2}".format(hex(self.index)[2:])

    def __str__(self):
        return self.name

    def __hash__(self):
        return self.index

    def __eq__(self, other):
        if type(other) == str:
            return self.name == other
        else:
            return self.index == other.index
