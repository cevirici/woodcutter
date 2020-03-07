from .Gamestate import *
from .Pile import *
from .Cards import *


def initializeSupply(supplyString):
    piles = supplyString.split("~")
    piles = {int(i.split(':')[1]): int(i.split(':')[0]) for i in piles}
    handled = set()
    state = Gamestate()

    for index in piles:
        if index not in handled:
            handled.add(index)
            cardName = CardNames(index)
            card = Cards[cardName]

            # Look for BM cards
            associates = []
            for i in piles:
                if CardNames(i) in card.pileCards:
                    handled.add(i)
                    associates.extend([CardNames(i) for j in range(piles[i])])

            if card.initialZone == NeutralZones.SUPPLY and \
                    len(associates) == 1:
                state.addCard(cardName, NeutralZones.BLACK_MARKET,
                              CardNames.BLACK_MARKET_PILE)

            else:
                if (card.orderedPile):
                    associates.sort(key=lambda c: c.value)
                pile = Pile(card.keyCard, associates, card.orderedPile)
                state.newPile(pile, card.initialZone)
