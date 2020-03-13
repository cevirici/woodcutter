from .Gamestate import *
from .Pile import *
from .Card import *
from .GenericActions import *


class ParsedLine:
    def __init__(self, indent, pred, player, items, args):
        self.indent = indent
        self.pred = pred
        self.player = player
        self.items = items
        self.args = args


class Parser:
    def __init__(self, version):
        self.cards, self.preds = getInfo(version)

    def initializeSupply(self, supplyString):
        piles = {}
        for item in supplyString.split("~"):
            if item:
                c, i = item.split(':')
                piles[self.cards[int(i)]] = int(c)

        handled = set()
        state = Gamestate()
        index = 0

        for cardName in piles:
            if cardName not in handled:
                handled.add(cardName)
                cardInfo = getCardInfo(cardName)
                pileCards = cardInfo.getPileCards()
                initialZone = cardInfo.initialZone

                # Look for BM cards
                associates = []
                for otherCard in piles:
                    if otherCard in pileCards:
                        handled.add(otherCard)
                        for j in range(piles[otherCard]):
                            associates.append(Card(otherCard, index))
                            index += 1

                if initialZone == NeutralZones.SUPPLY and len(associates) == 1:
                    state.addCard(Card(cardName, index),
                                  NeutralZones.BLACK_MARKET,
                                  "Black Market Pile")
                    index += 1
                else:
                    pile = Pile(cardInfo.getKeyCard(), associates)
                    state.newPile(pile, initialZone)
        return state

    def parse_items(self, inString):
        items = inString.split("+")
        output = []

        for item in items:
            parts = item.split(":")
            if len(parts) == 2:
                for i in range(int(parts[0])):
                    output.append(self.cards[int(parts[1])])
        return output

    def parse_arg(self, arg, parse=False):
        if ":" in arg:
            return [int(i) for i in arg.split(":")]
        elif parse:
            return self.cards[int(arg)]
        else:
            return int(arg)

    def parseLog(self, logString):
        logLines = logString.split('~')
        parsedLines = []
        parseablePreds = ["WISH_CORRECT", "WISH_WRONG"]

        for line in logLines:
            indent, pred, player, items, args = line.split("|")
            pred = self.preds[int(pred)]
            shouldParse = pred in parseablePreds
            args = [self.parse_arg(a, shouldParse) for
                    a in args.split("+")] if args else []

            parsedLines.append(ParsedLine(
                int(indent),
                pred,
                int(player) - 1,
                self.parse_items(items),
                args
            ))
        return parsedLines
