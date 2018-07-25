from .classes import *
from .standards import *
from copy import deepcopy

def fullRepair(inLog, moveTree, gameStates):
    changed = False
    currLog = inLog
    repairers = [repairRepay]
    for repairer in repairers:
        output = repairer(currLog, moveTree, gameStates)
        currLog = output[0]
        changed = output[1] or changed

    return (currLog, changed)


def snip(rawLog, snips):
    # snips are tuples of the form (decision, player, indent, pred, items)
    logStrings = rawLog.split('~')
    for snip in snips:
        outstr = '{}{}{:0>2}{}'.format(hex(snip[1].player + 1)[2:],
                                       hex(snip[1].indent)[2:],
                                       hex(snip[1].pred)[2:],
                                       snip[1].items)
        print('replacing {} with {}'.format(logStrings[snip[0]], outstr))
        logStrings[snip[0]] = outstr

    return '~'.join(logStrings)


def repairGear(rawLog, moveTree, gameStates):
    for turn in moveTree:
        pass


def repairRepay(rawLog, moveTree, gameStates):
    snips = []
    currIndex = 0

    def scan_chunk(chunk):
        nonlocal currIndex, snips
        if chunk[0].predName() == "REPAY DEBT" and\
           ARGUMENT_CARD in chunk[0].items:
            newLine = deepcopy(chunk[0])
            newLine.items.insert(standardNames.index('debt'), newLine.items[ARGUMENT_CARD])
            newLine.items = newLine.items.strip()
            snips.append((currIndex, newLine))

        currIndex += 1
        for subchunk in chunk[1:]:
            scan_chunk(subchunk)

    for turn in moveTree:
        scan_chunk(turn)

    outLog = snip(rawLog, snips)
    return (outLog, len(snips) > 0)
