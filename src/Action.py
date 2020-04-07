# -*- coding: utf-8 -*-


class Action:
    name = "Unknown Action"

    def __init__(self):
        pass

    def __repr__(self):
        return self.name

    def act(self, state, log):
        return None
