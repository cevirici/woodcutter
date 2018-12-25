from .classes import *
from .Standards import *
from .Actions import INTRINSIC_EXCEPTIONS


def parse_single_line(moves, i, blockLength, state):
    move = moves[i]
    realExceptions = set()
    for exception in state.exceptions:
        if exception.lifespan > 0:
            exception.lifespan -= 1
        if exception.lifespan != 0:
            realExceptions.add(exception)
    state.exceptions = realExceptions

    excOrder = sorted(state.exceptions, key=lambda x: -x.priority)
    actionPriority = 0

    for exception in excOrder:
        if actionPriority > exception.priority:
            break
        elif exception.condition(move):
            if move.indent in exception.indents or not exception.indents:
                actionPriority = exception.priority
                exception.action(moves, i, blockLength, state)
                if not exception.persistent:
                    state.exceptions.remove(exception)


def parse_everything(gameMoves, blockLengths, supply):
    # Setup starting state
    startState = GameState()
    for card in supply:
        destination = 'SUPPLY'
        for t in Cards[card].types:
            if t in 'elpb':
                destination = None
            elif t == 'z':
                destination = 'TRASH'
        if destination:
            startState[destination] += Cardstack({card: supply[card]})

    gameStates = [startState]
    startState.exceptions = INTRINSIC_EXCEPTIONS
    for i, blockLength in enumerate(blockLengths):
        state = deepcopy(gameStates[-1])
        # set game phase - if it's a base action set the phase to 0
        if gameMoves[i].indent == 0:
            state.phase = 4
        parse_single_line(gameMoves, i, blockLength, state)
        gameStates.append(state)

    return gameStates
