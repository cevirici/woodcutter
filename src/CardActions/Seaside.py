# -*- coding: utf-8 -*-
from .CardInfo import CardInfo
from woodcutter.src.Card import *
from woodcutter.src.Action import Action


class AMBASSADOR(CardInfo):
    names = ["Ambassador", "Ambassadors", "a Ambassador"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [maybe(gain()), maybe(returnCards()), hasCards(revealHand())]
        state.candidates = state.stack.pop()


class BAZAAR(CardInfo):
    names = ["Bazaar", "Bazaars", "a Bazaar"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [getCoin(), getAction(), drawN(1)]
        state.candidates = state.stack.pop()
        return state


class CARAVAN(CardInfo):
    names = ["Caravan", "Caravans", "a Caravan"]
    types = [Types.ACTION, Types.DURATION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        targetThrone = -1
        for throne in state.thrones:
            if state.thrones[throne] == cardIndex:
                targetThrone = throne

        for card in state.zones[PlayerZones.PLAY][state.player][0].cards:
            if card.index == cardIndex or card.index == targetThrone:
                card.stayingOut = max(card.stayingOut, 1)

        state.turnStarts.append(["Caravan"])
        state.stack += [getAction(), drawN(1)]
        state.candidates = state.stack.pop()
        return state

    def onDuration(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]

        deckCount = state.zoneCount(PlayerZones.DECK)
        discardCount = state.zoneCount(PlayerZones.DISCARD)
        if deckCount == 0 and discardCount > 0:
            # Shuffle then go again
            state.candidates = [shuffle()]
            state.stack += [onDuration(self)]
            return state
        elif logLine.pred == "DRAW_FROM_CARAVAN":
            amount = len(logLine.items)
            state.logLine += 1
            if not state.moveCards(logLine.items, PlayerZones.DECK, PlayerZones.HAND):
                return None

            i = 0
            remaining = []
            for d in state.turnStarts:
                if d[0] == "Caravan" and i < amount:
                    i += 1
                else:
                    remaining.append(d)
            state.turnStarts = remaining

            if i < amount:
                return None
            else:
                state.candidates = state.stack.pop()
                return state
        else:
            return None


class CUTPURSE(CardInfo):
    names = ["Cutpurse", "Cutpurses", "a Cutpurse"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class EMBARGO(CardInfo):
    names = ["Embargo", "Embargos", "an Embargo"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class EXPLORER(CardInfo):
    names = ["Explorer", "Explorers", "an Explorer"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class FISHING_VILLAGE(CardInfo):
    names = ["Fishing Village", "Fishing Villages", "a Fishing Village"]
    types = [Types.ACTION, Types.DURATION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class GHOST_SHIP(CardInfo):
    names = ["Ghost Ship", "Ghost Ships", "a Ghost Ship"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class HAVEN(CardInfo):
    names = ["Haven", "Havens", "a Haven"]
    types = [Types.ACTION, Types.DURATION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class ISLAND(CardInfo):
    names = ["Island", "Islands", "an Island"]
    types = [Types.ACTION, Types.VICTORY]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class LIGHTHOUSE(CardInfo):
    names = ["Lighthouse", "Lighthouses", "a Lighthouse"]
    types = [Types.ACTION, Types.DURATION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class LOOKOUT(CardInfo):
    names = ["Lookout", "Lookouts", "a Lookout"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class MERCHANT_SHIP(CardInfo):
    names = ["Merchant Ship", "Merchant Ships", "a Merchant Ship"]
    types = [Types.ACTION, Types.DURATION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class NATIVE_VILLAGE(CardInfo):
    names = ["Native Village", "Native Villages", "a Native Village"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class NAVIGATOR(CardInfo):
    names = ["Navigator", "Navigators", "a Navigator"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class OUTPOST(CardInfo):
    names = ["Outpost", "Outposts", "an Outpost"]
    types = [Types.ACTION, Types.DURATION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class PEARL_DIVER(CardInfo):
    names = ["Pearl Diver", "Pearl Divers", "a Pearl Diver"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class PIRATE_SHIP(CardInfo):
    names = ["Pirate Ship", "Pirate Ships", "a Pirate Ship"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SALVAGER(CardInfo):
    names = ["Salvager", "Salvagers", "a Salvager"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SEA_HAG(CardInfo):
    names = ["Sea Hag", "Sea Hags", "a Sea Hag"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SMUGGLERS(CardInfo):
    names = ["Smugglers", "Smugglers", "a Smugglers"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TACTICIAN(CardInfo):
    names = ["Tactician", "Tacticians", "a Tactician"]
    types = [Types.ACTION, Types.DURATION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TREASURE_MAP(CardInfo):
    names = ["Treasure Map", "Treasure Maps", "a Treasure Map"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TREASURY(CardInfo):
    names = ["Treasury", "Treasuries", "a Treasury"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WAREHOUSE(CardInfo):
    names = ["Warehouse", "Warehouses", "a Warehouse"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WHARF(CardInfo):
    names = ["Wharf", "Wharves", "a Wharf"]
    types = [Types.ACTION, Types.DURATION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state
