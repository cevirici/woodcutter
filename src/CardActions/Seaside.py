# -*- coding: utf-8 -*-
from copy import deepcopy
from .CardInfo import CardInfo
from woodcutter.src.Card import *
from woodcutter.src.Action import Action
from woodcutter.src.GenericActions import *


class AMBASSADOR(CardInfo):
    names = ["Ambassador", "Ambassadors", "a Ambassador"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            [maybe(gain())],
            [maybe(returnCards())],
            [hasCards(revealHand())],
        ]
        state.candidates = state.stack.pop()


class BAZAAR(CardInfo):
    names = ["Bazaar", "Bazaars", "a Bazaar"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[getCoin()], [getAction()], [drawN(1)]]
        state.candidates = state.stack.pop()
        return state


class caravanDuration(Action):
    name = "Caravan Duration"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]

        deckCount = state.zoneCount(PlayerZones.DECK)
        discardCount = state.zoneCount(PlayerZones.DISCARD)
        if deckCount == 0 and discardCount > 0:
            # Shuffle then go again
            state.candidates = [shuffle()]
            state.stack += [[onDuration(self)]]
            return state
        elif logLine.pred == "DRAW_FROM_CARAVAN":
            amount = len(logLine.items)
            state.logLine += 1
            if not state.moveCards(logLine.items, PlayerZones.DECK, PlayerZones.HAND):
                return None

            i = 0
            remaining = []
            for d in state.flags:
                if d[1] == "Caravan" and i < amount:
                    i += 1
                else:
                    remaining.append(d)
            state.flags = remaining

            if i < amount:
                return None
            else:
                state.candidates = state.stack.pop()
                return state
        else:
            return None


class CARAVAN(CardInfo):
    names = ["Caravan", "Caravans", "a Caravan"]
    types = [Types.ACTION, Types.DURATION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        card = state.cards[cardIndex]
        card.stayingOut = max(card.stayingOut, 1)

        state.flags.append((FlagTypes.START_OF_TURN, "Caravan", caravanDuration()))
        state.stack += [[getAction()], [drawN(1)]]
        state.candidates = state.stack.pop()
        return state


class CUTPURSE(CardInfo):
    names = ["Cutpurse", "Cutpurses", "a Cutpurse"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            [maybe(discard()), revealHand()],
            [getCoin()],
            [reactToAttack()],
        ]
        state.candidates = state.stack.pop()
        return state


class embargoOnBuy(Action):
    name = "Embargo On Buy"

    def __init__(self, target):
        self.target = target

    def act(self, state, log):
        state = deepcopy(state)
        for pile in state.piles:
            if self.target in pile.cards:
                if pile.embargoTokens > 0:
                    state.stack += [[conditionally(hasCard("Curse"), gain())]]
                break

        state.candidates = state.stack.pop()
        return state


class embargoPile(Action):
    def __init__(self, pile):
        self.name = "Embargo {} Pile".format(pile.cards[0])
        self.pile = pile

    def act(self, state, log):
        state = deepcopy(state)
        self.pile.embargoTokens += 1
        state.flags.append((FlagTypes.BUY, "Embargo", embargoOnBuy))
        state.candidates = state.stack.pop()
        return state


class EMBARGO(CardInfo):
    names = ["Embargo", "Embargos", "an Embargo"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.append([embargoPile(p) for p in state.piles])
        state.stack += [
            [maybe(trash(PlayerZones.PLAY, NeutralZones.TRASH))],
            [getCoin()],
        ]
        state.candidates = state.stack.pop()
        return state


class explorerProc(Action):
    name = "Explorer Procced"

    def act(self, state, log):
        state = deepcopy(state)
        state.stack += [
            [maybe(gain(NeutralZones.SUPPLY, PlayerZones.HAND))],
            [revealHand()],
        ]
        state.candidates = state.stack.pop()
        return state


class EXPLORER(CardInfo):
    names = ["Explorer", "Explorers", "an Explorer"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.candidates = [
            explorerProc(),
            maybe(gain(NeutralZones.SUPPLY, PlayerZones.HAND)),
        ]
        return state


class fvCoin(Action):
    name = "Fishing Village Coin"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]

        if logLine.pred == "COIN_FROM_FISHING_VILLAGE":
            state.coins += 1
        elif logLine.pred == "RETURNS_MINUS_COIN_TOKEN":
            pass
        else:
            return None
        state.logLine += 1
        state.candidates = state.stack.pop()
        return state


class fvDuration(Action):
    name = "Fishing Village Duration"

    def act(self, state, log):
        state = deepcopy(state)
        state.stack += [[fvCoin()], [getAction()]]

        for d in state.flags:
            if d[1] == "Fishing Village":
                state.flags.remove(d)
                break

        state.candidates = state.stack.pop()
        return state


class FISHING_VILLAGE(CardInfo):
    names = ["Fishing Village", "Fishing Villages", "a Fishing Village"]
    types = [Types.ACTION, Types.DURATION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        card = state.cards[cardIndex]
        card.stayingOut = max(card.stayingOut, 1)

        state.flags.append((FlagTypes.START_OF_TURN, "Fishing Village", fvDuration()))
        state.stack += [[getCoin()], [getAction()]]
        state.candidates = state.stack.pop()
        return state


class GHOST_SHIP(CardInfo):
    names = ["Ghost Ship", "Ghost Ships", "a Ghost Ship"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[maybe(topdeck())][drawN(2)][reactToAttack()]]
        state.candidates = state.stack.pop()
        return state


class havenDuration(Action):
    def __init__(self, target):
        self.name = "Haven Duration ({})".format(target)
        self.target = target

    def act(self, state, log):
        if logLine.pred == "PUT_IN_HAND_FROM_HAVEN":
            state.logLine += 1
            if not state.moveCards(
                logLine.items, PlayerZones.SET_ASIDE, PlayerZones.HAND
            ):
                return None

            unhandled = logLine.items
            remaining = []
            for d in state.flags:
                if d[1] == "Haven" and d[3] in unhandled:
                    unhandled.remove(d[1])
                else:
                    remaining.append(d)
            state.flags = remaining

            if unhandled:
                return None
            else:
                state.candidates = state.stack.pop()
                return state
        else:
            return None


class havenSet(Action):
    name = "Haven Setaside"

    def __init__(self, cardIndex):
        self.cardIndex = cardIndex

    def act(self, state, log):
        logLine = log[state.logLine]
        if logLine.pred == "SET_ASIDE":
            state = deepcopy(state)
            card = state.cards[self.cardIndex]
            card.stayingOut = max(card.stayingOut, 1)

            target = state.moveCards(
                logLine.items, PlayerZones.HAND, PlayerZones.SET_ASIDE
            )
            if not target:
                return None
            else:
                state.flags.append(
                    (
                        FlagTypes.START_OF_TURN,
                        "Haven",
                        havenDuration(target.name),
                        target.name,
                    )
                )
            return state
        else:
            return None


class HAVEN(CardInfo):
    names = ["Haven", "Havens", "a Haven"]
    types = [Types.ACTION, Types.DURATION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[hasCards(havenSet(cardIndex))], [getAction()], [drawN(1)]]
        state.candidates = state.stack.pop()
        return state


class islandSet(Action):
    name = "Island Set Aside"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]

        if logLine.pred == "PUT_ON_MAT":
            state.logLine += 1
            if state.moveCards(logLine.items, PlayerZones.HAND, PlayerZones.SET_ASIDE):
                state.candidates = state.stack.pop()
                return state
        return None


class islandSetSelf(Action):
    name = "Island Set Aside (itself)"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]

        if logLine.pred == "PUT_ON_MAT":
            state.logLine += 1
            if state.moveCards(logLine.items, PlayerZones.PLAY, PlayerZones.SET_ASIDE):
                state.candidates = state.stack.pop()
                return state
        return None


class ISLAND(CardInfo):
    names = ["Island", "Islands", "an Island"]
    types = [Types.ACTION, Types.VICTORY]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [hasCards(islandSet()), islandSetSelf()]
        state.candidates = state.stack.pop()
        return state


class lighthouseDuration(Action):
    name = "Lighthouse Duration"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]

        if logLine.pred == "RETURNS_MINUS_COIN_TOKEN":
            amount = 1

        elif logLine.pred == "COIN_FROM_LIGHTHOUSE":
            amount = int(logLine.args[0])
            state.coins += amount

            return state
        else:
            return None

        state.logLine += 1
        state.candidates = state.stack.pop()

        i = 0
        remaining = []
        for d in state.flags:
            if d[1] == "Lighthouse" and i < amount:
                i += 1
            else:
                remaining.append(d)
        state.flags = remaining

        return state


class LIGHTHOUSE(CardInfo):
    names = ["Lighthouse", "Lighthouses", "a Lighthouse"]
    types = [Types.ACTION, Types.DURATION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        card = state.cards[cardIndex]
        card.stayingOut = max(card.stayingOut, 1)

        state.flags.append(["Lighthouse", lighthouseDuration()])
        state.stack += [[getCoin()], [getAction()]]
        state.candidates = state.stack.pop()
        return state


class lookoutLook(Action):
    name = "Lookout Look At"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player
        deckCount = state.zoneCount(PlayerZones.DECK)
        discardCount = state.zoneCount(PlayerZones.DISCARD)

        if deckCount < 3 and discardCount > 0:
            # Shuffle then go again
            state.candidates = [shuffle()]
            state.stack.append([self])
            return state
        elif deckCount > 0:
            if log[state.logLine].pred == "LOOK_AT":
                state.logLine += 1
                amount = len(logLine.items)
                if not state.moveCards(
                    logLine.items, PlayerZones.DECK, PlayerZones.DECK
                ):
                    return None

                if amount > 2:
                    state.stack.append([topdeck(PlayerZones.DECK)])
                if amount > 1:
                    state.stack.append([discard(PlayerZones.DECK)])
                state.stack.append([trash(PlayerZones.DECK)])
            else:
                return None
        state.candidates = state.stack.pop()
        return state


class LOOKOUT(CardInfo):
    names = ["Lookout", "Lookouts", "a Lookout"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[lookoutLook()], [getAction()]]
        state.candidates = state.stack.pop()
        return state


class msDuration(Action):
    name = "Merchant Ship Duration"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]

        if logLine.pred == "RETURNS_MINUS_COIN_TOKEN":
            amount = 1
            state.logLine += 1
            logLine = log[state.logLine]

        if logLine.pred == "COIN_FROM_MERCHANT_SHIP":
            amount += int(logLine.args[0])
            state.coins += int(logLine.args[0])

            return state
        else:
            return None

        state.logLine += 1
        state.candidates = state.stack.pop()

        i = 0
        remaining = []
        for d in state.flags:
            if d[1] == "Merchant Ship" and i < amount:
                i += 2
            else:
                remaining.append(d)
        state.flags = remaining

        return state


class MERCHANT_SHIP(CardInfo):
    names = ["Merchant Ship", "Merchant Ships", "a Merchant Ship"]
    types = [Types.ACTION, Types.DURATION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        card = state.cards[cardIndex]
        card.stayingOut = max(card.stayingOut, 1)

        state.flags.append((FlagTypes.START_OF_TURN, "Merchant Ship", msDuration()))
        state.stack += [[getCoin()]]
        state.candidates = state.stack.pop()
        return state


class NATIVE_VILLAGE(CardInfo):
    names = ["Native Village", "Native Villages", "a Native Village"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[maybe(setAside()), maybe(putInHand())], [getAction()]]
        state.candidates = state.stack.pop()
        return state


class NAVIGATOR(CardInfo):
    names = ["Navigator", "Navigators", "a Navigator"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            [maybe(discard(PlayerZones.DECK)), topdeck(PlayerZones.DECK)][lookAtN(5)],
            [getCoin()],
        ]
        state.candidates = state.stack.pop()
        return state


class OUTPOST(CardInfo):
    names = ["Outpost", "Outposts", "an Outpost"]
    types = [Types.ACTION, Types.DURATION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)

        if logLine.pred in [
            "OUTPOST_FAIL_PREVIOUS_TURN",
            "OUTPOST_FAIL_ALREADY_PLAYED",
            "OUTPOST_FAIL_NOT_NAMED_OUTPOST",
        ]:
            state.logLine += 1
        else:
            card = state.cards[cardIndex]
            card.stayingOut = max(card.stayingOut, 1)
            state.flags.append((FlagTypes.CLEANUP, "Outpost", cleanupDraw(3)))

        state.candidates = state.stack.pop()
        return state


class PEARL_DIVER(CardInfo):
    names = ["Pearl Diver", "Pearl Divers", "a Pearl Diver"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[maybe(topdeck())], [lookAtN(1)], [getAction()], [drawN(1)]]
        state.candidates = state.stack.pop()
        return state


class PIRATE_SHIP(CardInfo):
    names = ["Pirate Ship", "Pirate Ships", "a Pirate Ship"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[maybe(trashAttack()), getCoin()][reactToAttack()]]
        state.candidates = state.stack.pop()
        return state


class SALVAGER(CardInfo):
    names = ["Salvager", "Salvagers", "a Salvager"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[maybe(getCoin())], [hasCards(trash())], [getBuy()]]
        state.candidates = state.stack.pop()
        return state


class SEA_HAG(CardInfo):
    names = ["Sea Hag", "Sea Hags", "a Sea Hag"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [
            [maybe(gain())],
            [maybe(discard(PlayerZones.DECK))],
            [reactToAttack()],
        ]
        state.candidates = state.stack.pop()
        return state


class SMUGGLERS(CardInfo):
    names = ["Smugglers", "Smugglers", "a Smugglers"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.candidates = [maybe(gain())]
        return state


class tacticianDuration(Action):
    name = "Tactician Duration"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]

        state.player = logLine.player
        deckCount = state.zoneCount(PlayerZones.DECK)
        discardCount = state.zoneCount(PlayerZones.DISCARD)

        if deckCount < 5 and discardCount > 0:
            # Shuffle then go again
            state.candidates = [shuffle()]
            state.stack.append([self])
            return state
        elif deckCount > 0:
            if log[state.logLine].pred == "CARDS_BUY_ACTION_FROM_TACTICIAN":
                state.logLine += 1
                if not state.moveCards(
                    logLine.items, PlayerZones.DECK, PlayerZones.HAND
                ):
                    return None
            else:
                return None

        state.stack += [[getBuy()], [getAction()]]

        for d in state.flags:
            if d[1] == "Tactician":
                state.flags.remove(d)
                break

        state.candidates = state.stack.pop()
        return state


class TACTICIAN(CardInfo):
    names = ["Tactician", "Tacticians", "a Tactician"]
    types = [Types.ACTION, Types.DURATION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)

        if logLine.pred == "TACTICIAN_FAIL":
            state.logLine += 1
        else:
            state.flags.append(
                (FlagTypes.START_OF_TURN, "Tactician", tacticianDuration())
            )
            card = state.cards[cardIndex]
            card.stayingOut = max(card.stayingOut, 1)

        state.candidates = state.stack.pop()
        return state


class tmapProc(Action):
    name = "Treasure Map Accepted"

    def act(self, state, log):
        state = deepcopy(state)
        state.stack += [
            [hasCard("Gold", gain(NeutralZones.SUPPLY, PlayerZones.DECK))],
            [trash()],
            [trash(PlayerZones.Play, NeutralZones.TRASH)],
        ]
        state.candidates = state.stack.pop()
        return state


class TREASURE_MAP(CardInfo):
    names = ["Treasure Map", "Treasure Maps", "a Treasure Map"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.candidates = [
            maybe(trash(PlayerZones.Play, NeutralZones.TRASH)),
            tmapProc(),
        ]
        return state


class treasuryCleanup(Action):
    name = "Treasury Cleanup"

    def act(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.logLine += 1

        if logLine.pred == "TOPDECK":
            amount = len(logLine.items)
            if logLine.items[0] != "Treasury":
                return None
            if not state.moveCards(logLine.items, PlayerZones.PLAY, PlayerZones.DECK):
                return None

            i = 0
            remaining = []
            for d in state.flags:
                if d[1] == "Treasury" and i < amount:
                    i += 1
                else:
                    remaining.append(d)
            state.flags = remaining

            if i < amount:
                return None
            else:
                state.candidates = state.stack.pop()
                return state
        else:
            return None


class TREASURY(CardInfo):
    names = ["Treasury", "Treasuries", "a Treasury"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.flags.append((FlagTypes.CLEANUP, "Treasury", treasuryCleanup()))
        state.stack += [[getCoin()], [getAction()], [drawN(1)]]
        state.candidates = state.stack.pop()
        return state


class WAREHOUSE(CardInfo):
    names = ["Warehouse", "Warehouses", "a Warehouse"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[hasCards(discard())], [getAction()], [drawN(3)]]
        state.candidates = state.stack.pop()
        return state


class wharfDuration(Action):
    name = "Wharf Duration"

    def act(self, state, log):
        state = deepcopy(state)
        state.stack += [[getBuy()], [drawN(2)]]

        for d in state.flags:
            if d[1] == "Wharf":
                state.flags.remove(d)
                break

        state.candidates = state.stack.pop()
        return state


class WHARF(CardInfo):
    names = ["Wharf", "Wharves", "a Wharf"]
    types = [Types.ACTION, Types.DURATION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.flags.append((FlagTypes.START_OF_TURN, "Wharf", wharfDuration()))
        card.stayingOut = max(card.stayingOut, 1)
        state.stack += [[getBuy()], [drawN(2)]]
        state.candidates = state.stack.pop()
        return state
