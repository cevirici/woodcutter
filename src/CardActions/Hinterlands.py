# -*- coding: utf-8 -*-
from copy import deepcopy
from .CardInfo import CardInfo
from woodcutter.src.Card import *
from woodcutter.src.Action import Action
from woodcutter.src.GenericActions import *


class BORDER_VILLAGE(CardInfo):
    names = ["Border Village", "Border Villages", "a Border Village"]
    types = [Types.ACTION]
    cost = [6, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[getAction()], [drawN(1)]]
        state.candidates = state.stack.pop()
        return state

    def onGain(self, state, log):
        state = deepcopy(state)
        state.stack += [maybe(gain())]
        state.candidates = state.stack.pop()
        return state


class CACHE(CardInfo):
    names = ["Cache", "Caches", "a Cache"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onGain(self, state, log):
        state = deepcopy(state)
        state.stack += [hasCard("Copper", gain())]
        state.candidates = state.stack.pop()
        return state


class CARTOGRAPHER(CardInfo):
    names = ["Cartographer", "Cartographers", "a Cartographer"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            [maybe(topdeck(PlayerZones.DECK))],
            [maybe(discard(PlayerZones.DECK))],
            [maybe(discard(PlayerZones.DECK))],
            [lookAtN(4)],
            [drawN(1)],
        ]
        state.candidates = state.stack.pop()
        return state


class CROSSROADS(CardInfo):
    names = ["Crossroads", "Crossroads", "a Crossroads"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[maybe(getAction())], [drawN(99), drawN(1)], [revealHand()]]
        state.candidates = state.stack.pop()
        return state


class DEVELOP(CardInfo):
    names = ["Develop", "Develops", "a Develop"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[maybe(gain())], [maybe(gain())], [hasCards(trash())]]
        state.candidates = state.stack.pop()
        return state


class DUCHESS(CardInfo):
    names = ["Duchess", "Duchesses", "a Duchess"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        for p in range(PLAYER_COUNT):
            state.stack += [
                [
                    discard(PlayerZones.DECK, PlayerZones.DISCARD),
                    topdeck(PlayerZones.DECK, PlayerZones.DECK),
                ],
                [lookAt(1)],
            ]
        state.stack += [[getCoin()]]
        state.candidates = state.stack.pop()
        return state


class EMBASSY(CardInfo):
    names = ["Embassy", "Embassies", "an Embassy"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[hasCards(discard())], [drawN(5)]]
        state.candidates = state.stack.pop()
        return state

    def onGain(self, state, log):
        state = deepcopy(state)
        state.stack += [hasCard("Silver", gain())]
        state.candidates = state.stack.pop()
        return state


class FARMLAND(CardInfo):
    names = ["Farmland", "Farmlands", "a Farmland"]
    types = [Types.VICTORY]
    cost = [6, 0, 0]

    def onBuy(self, state, log):
        state = deepcopy(state)
        state.candidates.stack += [[maybe(gain())], [trash()]]
        return super().onBuy(state, log)


class fgTrigger(Action):
    name = "Fool's Gold Trigger"

    def __init__(self, target):
        self.target = target

    def act(self, state, log):
        state = deepcopy(state)
        if getCardInfo(self.target).hasType(Types.VICTORY):
            state.stack += [[reactToAttack()]]

        state.candidates = state.stack.pop()
        return state


class FOOLS_GOLD(CardInfo):
    names = ["Fool's Gold", "Fool's Golds", "a Fool's Gold"]
    types = [Types.TREASURE, Types.REACTION]
    cost = [2, 0, 0]

    def onGain(self, state, log):
        state = deepcopy(state)
        state.flags.append((FlagTypes.GAIN, "Fool's Gold", fgTrigger))
        state.candidates = state.stack.pop()
        return state

    def onReact(self, state, log):
        state = deepcopy(state)
        state.stack += [
            [hasCard("Gold", gain(NeutralZones.SUPPLY, PlayerZones.DECK))],
            [trash()],
        ]
        state.candidates = state.stack.pop()
        return state


class HAGGLER(CardInfo):
    names = ["Haggler", "Hagglers", "a Haggler"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [getCoin()]
        state.candidates = state.stack.pop()
        return state

    def onEnterPlay(self, state, cardIndex):
        state.flags.append((FlagTypes.BUY, "Haggler", mayGainAnother()))

    def onLeavePlay(self, state, cardIndex):
        for f in state.flags:
            if f[1] == "Haggler":
                state.flags.remove(f)
                return


class HIGHWAY(CardInfo):
    names = ["Highway", "Highways", "a Highway"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[getAction()], [drawN(1)]]
        state.candidates = state.stack.pop()
        return state

    def onEnterPlay(self, state, cardIndex):
        state.reductions.append((None, 1, cardIndex))

    def onLeavePlay(self, state, cardIndex):
        for r in state.reductions:
            if r[2] == cardIndex:
                state.reductions.remove(r)


class ILL_GOTTEN_GAINS(CardInfo):
    names = ["Ill-Gotten Gains", "Ill-Gotten Gains", "an Ill-Gotten Gains"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [maybe(gain(NeutralZones.SUPPLY, PlayerZones.HAND))]
        state.candidates = state.stack.pop()
        return state

    def onGain(self, state, log):
        state = deepcopy(state)
        state.stack += [hasCard("Curse", gain())]
        state.candidates = state.stack.pop()
        return state


class innShuffle(Action):
    name = "Inn Shuffle"

    def act(self, state, log):
        state = deepcopy(state)
        if log[state.logLine].pred == "REVEAL":
            state.logLine += 1
            if not state.moveCards(
                logLine.items, PlayerZones.DISCARD, PlayerZones.DECK
            ):
                return None
        if log[state.logLine].pred != "SHUFFLES":
            return None
        state.logLine += 1
        if log[state.logLine].pred != "SHUFFLE_INTO_DECK":
            return None
        state.logLine += 1
        state.candidates = state.stack.pop()
        return state


class INN(CardInfo):
    names = ["Inn", "Inns", "an Inn"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[hasCards(discard())], [getAction()], [drawN(2)]]
        state.candidates = state.stack.pop()
        return state

    def onGain(self, state, log):
        state = deepcopy(state)
        state.stack += [[innShuffle()], [lookAt()]]
        state.candidates = state.stack.pop()
        return state


class JACK_OF_ALL_TRADES(CardInfo):
    names = ["Jack of All Trades", "Jacks of All Trades", "a Jack of All Trades"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [maybe(trash())]
        handCount = state.zoneCount(PlayerZones.HAND)
        if handCount < 5:
            state.stack += [[drawN(5 - handCount)]]
        state.stack += [
            [maybe(discard(PlayerZones.DECK))],
            [lookAt(1)],
            [hasCard("Silver", gain())],
        ]
        state.candidates = state.stack.pop()
        return state


class MANDARIN(CardInfo):
    names = ["Mandarin", "Mandarins", "a Mandarin"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[hasCards(topdeck())], [getCoin()]]
        state.candidates = state.stack.pop()
        return state

    def onGain(self, state, log):
        state = deepcopy(state)
        state.stack += [[maybe(topdeck(PlayerZones.PLAY, PlayerZones.DECK))]]
        state.candidates = state.stack.pop()
        return state


class NOBLE_BRIGAND(CardInfo):
    names = ["Noble Brigand", "Noble Brigands", "a Noble Brigand"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[trashAttack()], [getCoin()], [reactToAttack()]]
        state.candidates = state.stack.pop()
        return state

    def onBuy(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[trashAttack()], [getCoin()]]
        return super().onBuy(state, log)


class NOMAD_CAMP(CardInfo):
    names = ["Nomad Camp", "Nomad Camps", "a Nomad Camp"]
    types = [Types.ACTION]
    cost = [4, 0, 0]
    gainDestination = PlayerZones.DECK

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[getCoin()], [getBuy()]]
        state.candidates = state.stack.pop()
        return state


class OASIS(CardInfo):
    names = ["Oasis", "Oases", "an Oasis"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[discard()], [getCoin()], [getAction()], [drawN(1)]]
        state.candidates = state.stack.pop()
        return state


class ORACLE(CardInfo):
    names = ["Oracle", "Oracles", "an Oracle"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[drawN(2)], [maybe(scry(2))], [scry(2)], [reactToAttack()]]
        state.candidates = state.stack.pop()
        return state


class MARGRAVE(CardInfo):
    names = ["Margrave", "Margraves", "a Margrave"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            [maybe(discard())],
            [maybe(drawN(1))],
            [getBuy()],
            [drawN(3)],
            [reactToAttack()],
        ]
        state.candidates = state.stack.pop()
        return state


class SCHEME(CardInfo):
    names = ["Scheme", "Schemes", "a Scheme"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.flags.append((FlagTypes.CLEANUP, "Scheme", topdeckerCleanup()))
        state.stack += [[getAction()], [drawN(1)]]
        state.candidates = state.stack.pop()
        return state


class SILK_ROAD(CardInfo):
    names = ["Silk Road", "Silk Roads", "a Silk Road"]
    types = [Types.VICTORY]
    cost = [4, 0, 0]


class smAccepted(Action):
    name = "Spice Merchant Accepted"

    def act(self, state, log):
        state = deepcopy(state)
        state.stack += [[getBuy(), getAction()], [getCoin(), drawN(2)], [trash()]]
        state.candidates = state.stack.pop()
        return state


class SPICE_MERCHANT(CardInfo):
    names = ["Spice Merchant", "Spice Merchants", "a Spice Merchant"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.candidates = [nothing(), smAccepted()]
        return state


class stablesAccepted(Action):
    name = "Stables Accepted"

    def act(self, state, log):
        state = deepcopy(state)
        state.stack += [[getAction()], [drawN(3)], [discard()]]
        state.candidates = state.stack.pop()
        return state


class STABLES(CardInfo):
    names = ["Stables", "Stables", "a Stables"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.candidates = [nothing(), stablesAccepted()]
        return state


class TRADER(CardInfo):
    names = ["Trader", "Traders", "a Trader"]
    types = [Types.ACTION, Types.REACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[maybe(gain())], [trash()]]
        state.candidates = state.stack.pop()
        return state

    def onReaction(self, state, log):
        state = deepcopy(state)
        state.candidates = [gain()]
        return state


class TUNNEL(CardInfo):
    names = ["Tunnel", "Tunnels", "a Tunnel"]
    types = [Types.VICTORY, Types.REACTION]
    cost = [3, 0, 0]

    def onDiscard(self, state, log):
        state = deepcopy(state)
        state.stack += [[reactToAttack()]]
        state.candidates = state.stack.pop()
        return state

    def onReact(self, state, log):
        state = deepcopy(state)
        state.stack += [[gain()], [reveal()]]
        state.candidates = state.stack.pop()
        return state
