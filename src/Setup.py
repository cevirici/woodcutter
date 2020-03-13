from .Gamestate import *
from .Pile import *
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

        for card in piles:
            if card not in handled:
                handled.add(card)
                cardInfo = getCardInfo(card)
                pileCards = cardInfo.getPileCards()
                initialZone = cardInfo.initialZone
                orderedPile = cardInfo.isOrderedPile

                # Look for BM cards
                associates = []
                for otherCard in piles:
                    if otherCard in pileCards:
                        handled.add(i)
                        associates += [otherCard for j in range(piles[card])]

                if initialZone == NeutralZones.SUPPLY and len(associates) == 1:
                    state.addCard(card, NeutralZones.BLACK_MARKET,
                                  "Black Market Pile")

                else:
                    if (orderedPile):
                        associates.sort(key=lambda c: c.value)
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

    def parseLog(self, logString):
        logLines = logString.split('~')
        parsedLines = []
        for line in logLines:
            indent, pred, player, items, args = line.split("|")
            parsedLines.append(ParsedLine(
                int(indent),
                self.preds[int(pred)],
                int(player) - 1,
                self.parse_items(items),
                args.split("+") if args else []
            ))
        return parsedLines
