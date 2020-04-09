# -*- coding: utf-8 -*-
from .CardInfo import CardInfo
from woodcutter.src.Card import *
from woodcutter.src.Action import Action


class BANK(CardInfo):
    names = ["Bank", "Banks", "a Bank"]
    types = [Types.TREASURE]
    cost = [7, 0, 0]


class BISHOP(CardInfo):
    names = ["Bishop", "Bishops", "a Bishop"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            [maybe(hasCards(trash()))],
            [getVP()],
            [hasCards(trash())],
            [getCoin()],
        ]
        state.candidates = state.stack.pop()
        return state


class COLONY(CardInfo):
    names = ["Colony", "Colonies", "a Colony"]
    types = [Types.VICTORY]
    cost = [11, 0, 0]


class CONTRABAND(CardInfo):
    names = ["Contraband", "Contrabands", "a Contraband"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [name(), getBuy()]
        state.candidates = state.stack.pop()
        return state


class COUNTING_HOUSE(CardInfo):
    names = ["Counting House", "Counting Houses", "a Counting House"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[maybe(putInHand())], [maybe(lookAt())], [lookAt()]]
        state.candidates = state.stack.pop()
        return state


class CITY(CardInfo):
    names = ["City", "Cities", "a City"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            [maybe(getCoin())],
            [maybe(getBuy())],
            [getAction()],
            [drawN(2), drawN(1)],
        ]
        state.candidates = state.stack.pop()
        return state


class EXPAND(CardInfo):
    names = ["Expand", "Expands", "an Expand"]
    types = [Types.ACTION]
    cost = [7, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[gain()], [hasCards(trash())]]
        state.candidates = state.stack.pop()
        return state


class FORGE(CardInfo):
    names = ["Forge", "Forges", "a Forge"]
    types = [Types.ACTION]
    cost = [7, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[maybe(gain())], [hasCards(trash())]]
        state.candidates = state.stack.pop()
        return state


class GRAND_MARKET(CardInfo):
    names = ["Grand Market", "Grand Markets", "a Grand Market"]
    types = [Types.ACTION]
    cost = [6, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[getCoin()], [getBuy()], [getAction()], [drawN(1)]]
        state.candidates = state.stack.pop()
        return state


class goonsVP(Action):
    name = "Goons VP"

    def __init__(self, target):
        pass

    def act(self, state, log):
        state = deepcopy(state)
        state.stack += [[getVP()]]
        state.candidates = state.stack.pop()
        return state


class GOONS(CardInfo):
    names = ["Goons", "Goons", "a Goons"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [6, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[maybe(discard())], [getCoin()], [getBuy()], [reactToAttack()]]
        state.candidates = state.stack.pop()
        return state

    def onEnterPlay(self, state, cardIndex):
        state.flags.append((FlagTypes.BUY, "Goons", goonsVP()))

    def onLeavePlay(self, state, cardIndex):
        for f in state.flags:
            if f[1] == "Goons":
                state.flags.remove(f)
                return


class hoardOnBuy(Action):
    name = "Hoard On Buy"

    def __init__(self, target):
        self.target = target

    def act(self, state, log):
        state = deepcopy(state)
        if getCardInfo(self.target).hasType(Types.VICTORY):
            state.stack += [[conditionally(hasCard("Gold"), gain())]]

        state.candidates = state.stack.pop()
        return state


class HOARD(CardInfo):
    names = ["Hoard", "Hoards", "a Hoard"]
    types = [Types.TREASURE]
    cost = [6, 0, 0]

    def onEnterPlay(self, state, cardIndex):
        state = deepcopy(state)
        state.flags.append((FlagTypes.BUY, "Hoard", hoardOnBuy()))
        state.candidates = state.stack.pop()
        return state

    def onLeavePlay(self, state, cardIndex):
        for f in state.flags:
            if f[1] == "Hoard":
                state.flags.remove(f)
                return


class KINGS_COURT(CardInfo):
    names = ["King's Court", "King's Courts", "a King's Court"]
    types = [Types.ACTION]
    cost = [7, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)

        logLine = log[state.logLine]
        state.player = logLine.player
        throne = state.cards[cardIndex]

        if logLine.pred == "PLAY" and len(logLine.items) == 1:
            target = logLine.items[0]
            state.logLine += 1

            card = state.moveCards([target], PlayerZones.HAND, PlayerZones.PLAY)[0]
            if card:
                card.master = throne
                throne.slaves.append(card)

                state.stack += [
                    [replay(card)],
                    [replay(card)],
                    [onPlay(card)],
                ]

        state.candidates = state.stack.pop()
        return state


class LOAN(CardInfo):
    names = ["Loan", "Loans", "a Loan"]
    types = [Types.TREASURE]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.candidates = [seek(trash(PlayerZones.DECK, NeutralZones.TRASH))]
        return state


class MINT(CardInfo):
    names = ["Mint", "Mints", "a Mint"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[maybe(gain())], [maybe(revealHand())]]
        state.candidates = state.stack.pop()
        return state

    def onBuy(self, state, log):
        state = deepcopy(state)
        state.candidates = [[trash(PlayerZones.PLAY, NeutralZones.TRASH)]]
        return super().onBuy(state, log)


class MONUMENT(CardInfo):
    names = ["Monument", "Monuments", "a Monument"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[getVP()], [getCoin()]]
        state.candidates = state.stack.pop()
        return state


class MOUNTEBANK(CardInfo):
    names = ["Mountebank", "Mountebanks", "a Mountebank"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            [maybe(gain())],
            [maybe(gain()), discard()],
            [getCoin()],
            [reactToAttack()],
        ]
        state.candidates = state.stack.pop()
        return state


class PEDDLER(CardInfo):
    names = ["Peddler", "Peddlers", "a Peddler"]
    types = [Types.ACTION]
    cost = [8, 0, 0]

    def onBuy(self, state, log):
        state = deepcopy(state)
        coinCost = self.cost[0]
        for (card, amount) in state.reductions:
            if card is None or card(self.names[0]):
                coinCost -= amount
        if state.phase in [Phases.TREASURE_PLAYING, Phases.BUY]:
            for card in state.zones[PlayerZones.PLAY][state.player]:
                if Type.ACTION in getCardInfo(card.name).types:
                    coinCost -= 2

        state.coins -= max(0, coinCost)
        state.buys -= 1
        if state.coins >= 0 and state.potions >= 0 and state.buys >= 0:
            state.candidates = state.stack.pop()
            return state

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[getCoin()], [getAction()], [drawN(1)]]
        state.candidates = state.stack.pop()
        return state


class PLATINUM(CardInfo):
    names = ["Platinum", "Platina", "a Platinum"]
    types = [Types.TREASURE]
    cost = [9, 0, 0]


def isAction(card):
    return Types.ACTION in getCardInfo(card).types


class QUARRY(CardInfo):
    names = ["Quarry", "Quarries", "a Quarry"]
    types = [Types.TREASURE]
    cost = [4, 0, 0]

    def onEnterPlay(self, state, cardIndex):
        state.reductions.append((isAction, 2, cardIndex))

    def onLeavePlay(self, state, cardIndex):
        for r in state.reductions:
            if r[2] == cardIndex:
                state.reductions.remove(r)


class RABBLE(CardInfo):
    names = ["Rabble", "Rabbles", "a Rabble"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            [maybe(topdeck(PlayerZones.DECK))],
            [maybe(discard(PlayerZones.DECK))],
            [maybe(revealN(3))],
            [drawN(3)],
            [reactToAttack()],
        ]
        state.candidates = state.stack.pop()
        return state


class ROYAL_SEAL(CardInfo):
    names = ["Royal Seal", "Royal Seals", "a Royal Seal"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onEnterPlay(self, state, cardIndex):
        state.flags.append((FlagTypes.GAIN, "Royal Seal", mayTopdeckGain))

    def onLeavePlay(self, state, cardIndex):
        for f in state.flags:
            if f[1] == "Royal Seal":
                state.flags.remove(f)
                return


class TALISMAN(CardInfo):
    names = ["Talisman", "Talismans", "a Talisman"]
    types = [Types.TREASURE]
    cost = [4, 0, 0]

    def onEnterPlay(self, state, cardIndex):
        state.flags.append((FlagTypes.BUY, "Talisman", mayGainAnother))

    def onLeavePlay(self, state, cardIndex):
        for f in state.flags:
            if f[1] == "Talisman":
                state.flags.remove(f)
                return


class TRADE_ROUTE(CardInfo):
    names = ["Trade Route", "Trade Routes", "a Trade Route"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[maybe(getCoin())], [hasCards(trash())], [getBuy()]]
        state.candidates = state.stack.pop()
        return state


class VAULT(CardInfo):
    names = ["Vault", "Vaults", "a Vault"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            [maybe(drawN(1))][maybe(discard())],
            [maybe(getCoin())],
            [maybe(discard())],
            [drawN(2)],
        ]
        state.candidates = state.stack.pop()
        return state


class VENTURE(CardInfo):
    names = ["Venture", "Ventures", "a Venture"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WATCHTOWER(CardInfo):
    names = ["Watchtower", "Watchtowers", "a Watchtower"]
    types = [Types.ACTION, Types.REACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [seek(play(PlayerZones.DECK))]
        state.candidates = state.stack.pop()
        return state


class WORKERS_VILLAGE(CardInfo):
    names = ["Worker's Village", "Worker's Villages", "a Worker's Village"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[getBuy()], [getAction()], [drawN(1)]]
        state.candidates = state.stack.pop()
        return state
