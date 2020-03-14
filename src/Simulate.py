# -*- coding: utf-8 -*-
from .Setup import *
from .GenericActions import *


def simulate(gamelog):
    # Use a backtracing algorithm to find a sequence of decisions
    # which work
    parser = Parser(gamelog.version)
    log = parser.parseLog(gamelog.log)

    state = parser.initializeSupply(gamelog.supply)
    state.candidates = [startGame()]
    states = [state]

    while states[-1].logLine < len(log) - 1:
        if len(states[-1].candidates) == 0:
            states.pop()
            if len(states) == 0:
                # Invalid log
                return []
        else:
            states[-1].move = states[-1].candidates.pop()
            attempt = states[-1].move.act(states[-1], log)
            # print(states[-1].logLine, states[-1].move)
            # print(log[states[-1].logLine].pred, log[states[-1].logLine].items)
            # print(log[states[-1].logLine].items, log[states[-1].logLine].args)
            # print(states[-1].buys, states[-1].coins, states[-1].reductions)
            # print(states[-1].stack)
            # print(states[-1].zones[PlayerZones.DISCARD][0])
            # print(states[-1].zones[PlayerZones.PLAY][0])
            # print(states[-1].zones[PlayerZones.HAND][0])
            # print(states[-1].zones[PlayerZones.DECK][0])
            # print(states[-1].coins, states[-1].buys)
            # print(states[-1].thrones)
            if attempt:
                states.append(attempt)
            else:
                print("Failed")

    return states
