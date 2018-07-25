from .classes import *
from .standards import *
from copy import deepcopy


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


def fullRepair(inLog, moveTree, gameStates):
    changed = False
    currLog = inLog
    repairers = [repairRepay, repairSave]
    allSnips = [repairer(currLog, moveTree, gameStates) for
                repairer in repairers]
    totalSnips = sum([len(x) for x in allSnips])
    print(allSnips)

    for snipList in allSnips:
        currLog = snip(currLog, snipList)

    return (currLog, totalSnips > 0)


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

    return snips


def repairSave(rawLog, moveTree, gameStates):
    snips = []
    currIndex = 0

    def scan_chunk(chunk, thisTurn):
        nonlocal currIndex, snips
        if chunk[0].predName() == "BUY" and\
           chunk[0].items.primary() == "Save":
            desc = chunk[1][0]
            if desc.predName() == "SET ASIDE WITH" and\
               CARD_CARD in desc.items:
                for rearCrawler in thisTurn[::-1]:
                    if rearCrawler[0].predName() == "PUT INHAND":
                        actualCard = rearCrawler[0].items
                        break

                newLine = deepcopy(desc)
                actualCard.insert(ARGUMENT_CARD, newLine.items[ARGUMENT_CARD])
                newLine.items = actualCard
                snips.append((currIndex + 1, newLine))


        currIndex += 1
        for subchunk in chunk[1:]:
            scan_chunk(subchunk, thisTurn)

    for turn in moveTree:
        scan_chunk(turn, turn)

    return snips
