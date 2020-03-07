from .Setup import *
from .GenericActions import *


def simulate(supplyString, logString):
    # Use a backtracing algorithm to find a sequence of decisions
    # which work
    log = logString.split('~')

    state = initializeSupply(supplyString)
    states = [state]

    while states[-1].logLine < len(logString) - 1:
        if len(states[-1].candidates) == 0:
            states.pop()
            if len(states) == 0:
                # Invalid log
                return []
        else:
            state.selectedMove = state.candidates.pop()
            states.append(state.selectedMove(states[-1], log))

    return states
