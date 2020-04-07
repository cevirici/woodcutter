# -*- coding: utf-8 -*-
from copy import deepcopy
from .CardInfo import CardInfo
from woodcutter.src.Card import *
from woodcutter.src.Action import Action
from woodcutter.src.GenericActions import *


class COURTYARD(CardInfo):
    names = ["Couryard", "Courtyards", "a Courtyard"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[hasCards(topdeck())], [drawN(3)]]
        state.candidates = state.stack.pop()
        return state


class CONSPIRATOR(CardInfo):
    names = ["Conspirator", "Conspirators", "a Conspirator"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[maybe(getAction())], [maybe(drawN(1))], [getCoin()]]
        state.candidates = state.stack.pop()
        return state


class COURTIER(CardInfo):
    names = ["Courtier", "Courtiers", "a Courtier"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            [maybe(gain())],
            [maybe(getCoin())],
            [maybe(getBuy())],
            [maybe(getAction())],
            [revealHand()],
        ]
        state.candidates = state.stack.pop()
        return state


class baronAccepted(Action):
    name = "Baron Accepted"

    def act(self, state, log):
        state = deepcopy(state)
        state.stack += [[getCoin()], [getBuy()], [discard()]]
        state.candidates = state.stack.pop()
        return state


class baronDeclined(Action):
    name = "Baron Declined"

    def act(self, state, log):
        state = deepcopy(state)
        state.candidates = [maybe(gain())]
        return state


class BARON(CardInfo):
    names = ["Baron", "Barons", "a Baron"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.candidates = [baronAccepted(), baronDeclined()]
        return state


class BRIDGE(CardInfo):
    names = ["Bridge", "Bridges", "a Bridge"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.reductions.append([None, 1])
        state.stack += [[getCoin()], [getBuy()]]
        state.candidates = state.stack.pop()
        return state


def diplomatCheck(state, log):
    return state.zoneCount(PlayerZones.HAND) <= 5


class DIPLOMAT(CardInfo):
    names = ["Diplomat", "Diplomats", "a Diplomat"]
    types = [Types.ACTION, Types.REACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[conditionally(diplomatCheck, getAction())], [drawN(2)]]
        state.candidates = state.stack.pop()
        return state

    def onReact(self, state, log):
        state = deepcopy(state)
        state.stack += [[hasCards(discard())], [drawN(2)]]
        state.candidates = state.stack.pop()
        return state


class DUKE(CardInfo):
    names = ["Duke", "Dukes", "a Duke"]
    types = [Types.VICTORY]
    cost = [5, 0, 0]


class HAREM(CardInfo):
    names = ["Harem", "Harems", "a Harem"]
    types = [Types.TREASURE, Types.VICTORY]
    cost = [6, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.candidates = state.stack.pop()
        state.coins += 2
        return state


class NOBLES(CardInfo):
    names = ["Nobles", "Nobles", "a Nobles"]
    types = [Types.ACTION, Types.VICTORY]
    cost = [6, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.candidates = [getAction(), drawN(3)]
        return state


class IRONWORKS(CardInfo):
    names = ["Ironworks", "Ironworks", "an Ironworks"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            maybe(drawN(1)),
            maybe(getCoin()),
            maybe(getAction()),
            maybe(gain()),
        ]
        state.candidates = state.stack.pop()
        return state


class LURKER(CardInfo):
    names = ["Lurker", "Lurkers", "a Lurker"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            maybe(trash(NeutralZones.SUPPLY, NeutralZones.TRASH)),
            maybe(gain(NeutralZones.TRASH, None)),
            getAction(),
        ]
        state.candidates = state.stack.pop()
        return state


class MASQUERADE(CardInfo):
    names = ["Masquerade", "Masquerades", "a Masquerade"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [maybe(trash())]
        state.stack += [maybe(passCard()) for p in range(PLAYER_COUNT)]
        state.stack.append(drawN(2))
        state.candidates = state.stack.pop()
        return state


class MILL(CardInfo):
    names = ["Mill", "Mills", "a Mill"]
    types = [Types.ACTION, Types.VICTORY]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [maybe(getCoin()), maybe(discard()), getAction(), drawN(1)]
        state.candidates = state.stack.pop()
        return state


class MINING_VILLAGE(CardInfo):
    names = ["Mining Village", "Mining Villages", "a Mining Village"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            maybe(getCoin()),
            maybe(trash(PlayerZones.PLAY, NeutralZones.TRASH)),
            getAction(),
            drawN(1),
        ]
        state.candidates = state.stack.pop()
        return state


class MINION(CardInfo):
    names = ["Minion", "Minions", "a Minion"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        for p in range(PLAYER_COUNT):
            state.stack += [maybe(drawN(4)), maybe(discard())]
        state.stack += [maybe(getCoin()), getAction(), reactToAttack()]
        state.candidates = state.stack.pop()
        return state


class PATROL(CardInfo):
    names = ["Patrol", "Patrols", "a Patrol"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            maybe(topdeck(PlayerZones.DECK, PlayerZones.DECK)),
            maybe(putInHand()),
            revealN(4),
            drawN(3),
        ]
        state.candidates = state.stack.pop()
        return state


class PAWN(CardInfo):
    names = ["Pawn", "Pawns", "a Pawn"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            maybe(getCoin()),
            maybe(getBuy()),
            maybe(getAction()),
            maybe(drawN(1)),
        ]
        state.candidates = state.stack.pop()
        return state


class replaceGain(Action):
    name = "Replace Gain"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player

        if logLine.pred == "GAIN":
            state.logLine += 1
            if len(logLine.items) == 1:
                target = logLine.items[0]
                cardInfo = getCardInfo(target)
                dest = cardInfo.gainDestination

                if cardInfo.hasType(Type.TREASURE) or cardInfo.hasType(Type.ACTION):
                    dest = PlayerZones.DECK
                if cardInfo.hasType(Type.VICTORY):
                    state.stack.append(gain())
                if not state.moveCards([target], self.src, dest):
                    return None

                state.stack.append(onGain(target))

                state.candidates = state.stack.pop()
                return state
        return None


class REPLACE(CardInfo):
    names = ["Replace", "Replaces", "a Replace"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [maybe(replaceGain()), hasCards(trash()), reactToAttack()]
        state.candidates = state.stack.pop()
        return state


class SECRET_PASSAGE(CardInfo):
    names = ["Secret Passage", "Secret Passages", "a Secret Passage"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [hasCards(topdeck()), getAction(), drawN(2)]
        state.candidates = state.stack.pop()
        return state


class SHANTY_TOWN(CardInfo):
    names = ["Shanty Town", "Shanty Towns", "a Shanty Town"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [maybe(drawN(2)), revealHand(), getAction()]
        state.candidates = state.stack.pop()
        return state


class STEWARD(CardInfo):
    names = ["Steward", "Stewards", "a Steward"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.candidates = [drawN(2), trash(), getCoin()]
        return state


class SWINDLER(CardInfo):
    names = ["Swindler", "Swindlers", "a Swindler"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            maybe(gain()),
            maybe(trash(PlayerZones.DECK, NeutralZones.TRASH)),
            getCoin(),
            reactToAttack(),
        ]
        state.candidates = state.stack.pop()
        return state


class TORTURER(CardInfo):
    names = ["Torturer", "Torturers", "a Torturer"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            maybe(discard()),
            maybe(gain(NeutralZones.SUPPLY, PlayerZones.HAND)),
            drawN(5),
            reactToAttack(),
        ]
        state.candidates = state.stack.pop()
        return state


class TRADING_POST(CardInfo):
    names = ["Trading Post", "Trading Posts", "a Trading Post"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            maybe(gain(NeutralZones.SUPPLY, PlayerZones.HAND)),
            hasCards(trash()),
        ]
        state.candidates = state.stack.pop()
        return state


class UPGRADE(CardInfo):
    names = ["Upgrade", "Upgrades", "an Upgrade"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [maybe(gain()), hasCards(trash()), getAction(), drawN(1)]
        state.candidates = state.stack.pop()
        return state


class WISHING_WELL(CardInfo):
    names = ["Wishing Well", "Wishing Wells", "a Wishing Well"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [maybe(wishWrong()), maybe(wishRight()), getAction(), drawN(1)]
        state.candidates = state.stack.pop()
        return state
