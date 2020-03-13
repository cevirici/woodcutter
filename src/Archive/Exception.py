# -*- coding: utf-8 -*-
class Exception:
    def __init__(
        self, condition, action, lifespan=-1, indents=[], priority=1, persistent=False
    ):
        self.condition = condition
        self.action = action
        self.lifespan = lifespan
        self.indents = indents
        self.priority = priority
        self.persistent = persistent
