# -*- coding: utf-8 -*-
from .CardInfo import CardInfo
from woodcutter.src.Card import *
from woodcutter.src.Action import Action


class RUINS(CardInfo):
    names = ["Ruins", "Ruins", "a Ruins"]
    types = [Types.ACTION, Types.RUINS]
    cost = [0, 0, 0]


class KNIGHTS(CardInfo):
    names = ["Knights", "Knights", "a Knights"]
    types = [Types.ACTION, Types.ATTACK, Types.KNIGHT]
    cost = [5, 0, 0]


class ABANDONED_MINE(CardInfo):
    names = ["Abandoned Mine", "Abandoned Mines", "an Abandoned Mine"]
    types = [Types.ACTION, Types.RUINS]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [getCoin()]
        state.candidates = state.stack.pop()
        return state


class ALTAR(CardInfo):
    names = ["Altar", "Altars", "an Altar"]
    types = [Types.ACTION]
    cost = [6, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += [[maybe(gain())], [hasCards(trash())]]
        state.candidates = state.stack.pop()
        return state


class ARMORY(CardInfo):
    names = ["Armory", "Armories", "an Armory"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.candidates = [[maybe(gain(NeutralZones.SUPPLY, PlayerZones.DECK))]]
        return state


class BAND_OF_MISFITS(CardInfo):
    names = ["Band of Misfits", "Bands of Misfits", "a Band of Misfits"]
    types = [Types.ACTION, Types.COMMAND]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)

        logLine = log[state.logLine]
        state.player = logLine.player
        master = state.cards[cardIndex]

        if logLine.pred == "PLAY" and len(logLine.items) == 1:
            target = logLine.items[0]
            state.logLine += 1

            card = state.moveCards([target], NeutralZones.SUPPLY, NeutralZones.SUPPLY)[
                0
            ]
            if card:
                card.master = master

                state.stack += [[onPlay(card)]]

        state.candidates = state.stack.pop()
        return state


class BANDIT_CAMP(CardInfo):
    names = ["Bandit Camp", "Bandit Camps", "a Bandit Camp"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class BEGGAR(CardInfo):
    names = ["Beggar", "Beggars", "a Beggar"]
    types = [Types.ACTION, Types.REACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CATACOMBS(CardInfo):
    names = ["Catacombs", "Catacombs", "a Catacombs"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class COUNT(CardInfo):
    names = ["Count", "Counts", "a Count"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class COUNTERFEIT(CardInfo):
    names = ["Counterfeit", "Counterfeits", "a Counterfeit"]
    types = [Types.TREASURE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CULTIST(CardInfo):
    names = ["Cultist", "Cultists", "a Cultist"]
    types = [Types.ACTION, Types.ATTACK, Types.LOOTER]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class DAME_ANNA(CardInfo):
    names = ["Dame Anna", "Dame Annas", "Dame Anna"]
    types = [Types.ACTION, Types.ATTACK, Types.KNIGHT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class DAME_JOSEPHINE(CardInfo):
    names = ["Dame Josephine", "Dame Josephines", "Dame Josephine"]
    types = [Types.ACTION, Types.ATTACK, Types.KNIGHT, Types.VICTORY]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class DAME_MOLLY(CardInfo):
    names = ["Dame Molly", "Dame Mollies", "Dame Molly"]
    types = [Types.ACTION, Types.ATTACK, Types.KNIGHT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class DAME_NATALIE(CardInfo):
    names = ["Dame Natalie", "Dame Natalies", "Dame Natalie"]
    types = [Types.ACTION, Types.ATTACK, Types.KNIGHT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class DAME_SYLVIA(CardInfo):
    names = ["Dame Sylvia", "Dame Sylvias", "Dame Sylvia"]
    types = [Types.ACTION, Types.ATTACK, Types.KNIGHT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class DEATH_CART(CardInfo):
    names = ["Death Cart", "Death Carts", "a Death Cart"]
    types = [Types.ACTION, Types.LOOTER]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class FEODUM(CardInfo):
    names = ["Feodum", "Feoda", "a Feodum"]
    types = [Types.VICTORY]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class FORAGER(CardInfo):
    names = ["Forager", "Foragers", "a Forager"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class FORTRESS(CardInfo):
    names = ["Fortress", "Fortresses", "a Fortress"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class GRAVEROBBER(CardInfo):
    names = ["Graverobber", "Graverobbers", "a Graverobber"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class HERMIT(CardInfo):
    names = ["Hermit", "Hermits", "a Hermit"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class HOVEL(CardInfo):
    names = ["Hovel", "Hovels", "a Hovel"]
    types = [Types.REACTION, Types.SHELTER]
    cost = [1, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class HUNTING_GROUNDS(CardInfo):
    names = ["Hunting Grounds", "Hunting Grounds", "a Hunting Grounds"]
    types = [Types.ACTION]
    cost = [6, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class IRONMONGER(CardInfo):
    names = ["Ironmonger", "Ironmongers", "an Ironmonger"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class JUNK_DEALER(CardInfo):
    names = ["Junk Dealer", "Junk Dealers", "a Junk Dealer"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class MADMAN(CardInfo):
    names = ["Madman", "Madmen", "a Madman"]
    types = [Types.ACTION]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class MARKET_SQUARE(CardInfo):
    names = ["Market Square", "Market Squares", "a Market Square"]
    types = [Types.ACTION, Types.REACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class MARAUDER(CardInfo):
    names = ["Marauder", "Marauders", "a Marauder"]
    types = [Types.ACTION, Types.ATTACK, Types.LOOTER]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class MERCENARY(CardInfo):
    names = ["Mercenary", "Mercenaries", "a Mercenary"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class MYSTIC(CardInfo):
    names = ["Mystic", "Mystics", "a Mystic"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class NECROPOLIS(CardInfo):
    names = ["Necropolis", "Necropolis", "a Necropolis"]
    types = [Types.ACTION, Types.SHELTER]
    cost = [1, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class OVERGROWN_ESTATE(CardInfo):
    names = ["Overgrown Estate", "Overgrown Estates", "an Overgrown Estate"]
    types = [Types.VICTORY, Types.SHELTER]
    cost = [1, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class PILLAGE(CardInfo):
    names = ["Pillage", "Pillages", "a Pillage"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class POOR_HOUSE(CardInfo):
    names = ["Poor House", "Poor Houses", "a Poor House"]
    types = [Types.ACTION]
    cost = [1, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class PROCESSION(CardInfo):
    names = ["Procession", "Processions", "a Procession"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class RATS(CardInfo):
    names = ["Rats", "Rats", "a Rats"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class REBUILD(CardInfo):
    names = ["Rebuild", "Rebuilds", "a Rebuild"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class ROGUE(CardInfo):
    names = ["Rogue", "Rogues", "a Rogue"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class RUINED_LIBRARY(CardInfo):
    names = ["Ruined Library", "Ruined Libraries", "a Ruined Library"]
    types = [Types.ACTION, Types.RUINS]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class RUINED_MARKET(CardInfo):
    names = ["Ruined Market", "Ruined Markets", "a Ruined Market"]
    types = [Types.ACTION, Types.RUINS]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class RUINED_VILLAGE(CardInfo):
    names = ["Ruined Village", "Ruined Villages", "a Ruined Village"]
    types = [Types.ACTION, Types.RUINS]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SAGE(CardInfo):
    names = ["Sage", "Sages", "a Sage"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SCAVENGER(CardInfo):
    names = ["Scavenger", "Scavengers", "a Scavenger"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SIR_BAILEY(CardInfo):
    names = ["Sir Bailey", "Sir Baileys", "Sir Bailey"]
    types = [Types.ACTION, Types.ATTACK, Types.KNIGHT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SIR_DESTRY(CardInfo):
    names = ["Sir Destry", "Sir Destries", "Sir Destry"]
    types = [Types.ACTION, Types.ATTACK, Types.KNIGHT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SIR_MARTIN(CardInfo):
    names = ["Sir Martin", "Sir Martins", "Sir Martin"]
    types = [Types.ACTION, Types.ATTACK, Types.KNIGHT]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SIR_MICHAEL(CardInfo):
    names = ["Sir Michael", "Sir Michaels", "Sir Michael"]
    types = [Types.ACTION, Types.ATTACK, Types.KNIGHT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SIR_VANDER(CardInfo):
    names = ["Sir Vander", "Sir Vanders", "Sir Vander"]
    types = [Types.ACTION, Types.ATTACK, Types.KNIGHT]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SPOILS(CardInfo):
    names = ["Spoils", "Spoils", "a Spoils"]
    types = [Types.TREASURE]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class STOREROOM(CardInfo):
    names = ["Storeroom", "Storerooms", "a Storeroom"]
    types = [Types.ACTION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SQUIRE(CardInfo):
    names = ["Squire", "Squires", "a Squire"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SURVIVORS(CardInfo):
    names = ["Survivors", "Survivors", "a Survivors"]
    types = [Types.ACTION, Types.RUINS]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class URCHIN(CardInfo):
    names = ["Urchin", "Urchins", "an Urchin"]
    types = [Types.ACTION, Types.ATTACK]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class VAGRANT(CardInfo):
    names = ["Vagrant", "Vagrants", "a Vagrant"]
    types = [Types.ACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WANDERING_MINSTREL(CardInfo):
    names = ["Wandering Minstrel", "Wandering Minstrels", "a Wandering Minstrel"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state
