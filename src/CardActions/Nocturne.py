# -*- coding: utf-8 -*-
from .CardInfo import CardInfo
from woodcutter.src.Card import *
from woodcutter.src.Action import Action


class THE_EARTHS_GIFT(CardInfo):
    names = ["The Earth's Gift", "The Earth's Gifts", "The Earth's Gift"]
    types = [Types.BOON]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class THE_FIELDS_GIFT(CardInfo):
    names = ["The Field's Gift", "The Field's Gifts", "The Field's Gift"]
    types = [Types.BOON]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class THE_FLAMES_GIFT(CardInfo):
    names = ["The Flame's Gift", "The Flame's Gifts", "The Flame's Gift"]
    types = [Types.BOON]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class THE_FORESTS_GIFT(CardInfo):
    names = ["The Forest's Gift", "The Forest's Gifts", "The Forest's Gift"]
    types = [Types.BOON]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class THE_MOONS_GIFT(CardInfo):
    names = ["The Moon's Gift", "The Moon's Gifts", "The Moon's Gift"]
    types = [Types.BOON]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class THE_MOUNTAINS_GIFT(CardInfo):
    names = ["The Mountain's Gift", "The Mountain's Gifts", "The Mountain's Gift"]
    types = [Types.BOON]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class THE_RIVERS_GIFT(CardInfo):
    names = ["The River's Gift", "The River's Gifts", "The River's Gift"]
    types = [Types.BOON]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class THE_SEAS_GIFT(CardInfo):
    names = ["The Sea's Gift", "The Sea's Gifts", "The Sea's Gift"]
    types = [Types.BOON]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class THE_SKYS_GIFT(CardInfo):
    names = ["The Sky's Gift", "The Sky's Gifts", "The Sky's Gift"]
    types = [Types.BOON]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class THE_SUNS_GIFT(CardInfo):
    names = ["The Sun's Gift", "The Sun's Gifts", "The Sun's Gift"]
    types = [Types.BOON]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class THE_SWAMPS_GIFT(CardInfo):
    names = ["The Swamp's Gift", "The Swamp's Gifts", "The Swamp's Gift"]
    types = [Types.BOON]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class THE_WINDS_GIFT(CardInfo):
    names = ["The Wind's Gift", "The Wind's Gifts", "The Wind's Gift"]
    types = [Types.BOON]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class BAD_OMENS(CardInfo):
    names = ["Bad Omens", "Bad Omens", "Bad Omens"]
    types = [Types.HEX]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class DELUSION(CardInfo):
    names = ["Delusion", "Delusions", "Delusion"]
    types = [Types.HEX]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class ENVY(CardInfo):
    names = ["Envy", "Envies", "Envy"]
    types = [Types.HEX]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class FAMINE(CardInfo):
    names = ["Famine", "Famines", "Famine"]
    types = [Types.HEX]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class FEAR(CardInfo):
    names = ["Fear", "Fears", "Fear"]
    types = [Types.HEX]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class GREED(CardInfo):
    names = ["Greed", "Greeds", "Greed"]
    types = [Types.HEX]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class HAUNTING(CardInfo):
    names = ["Haunting", "Hauntings", "Haunting"]
    types = [Types.HEX]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class LOCUSTS(CardInfo):
    names = ["Locusts", "Locusts", "Locusts"]
    types = [Types.HEX]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class MISERY(CardInfo):
    names = ["Misery", "Miseries", "Misery"]
    types = [Types.HEX]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class PLAGUE(CardInfo):
    names = ["Plague", "Plagues", "Plague"]
    types = [Types.HEX]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class POVERTY(CardInfo):
    names = ["Poverty", "Poverties", "Poverty"]
    types = [Types.HEX]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WAR(CardInfo):
    names = ["War", "Wars", "War"]
    types = [Types.HEX]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class MISERABLE(CardInfo):
    names = ["Miserable", "Miserables", "Miserable"]
    types = [Types.STATE]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TWICE_MISERABLE(CardInfo):
    names = ["Twice Miserable", "Twice Miserables", "Twice Miserable"]
    types = [Types.STATE]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class ENVIOUS(CardInfo):
    names = ["Envious", "Envious", "Envious"]
    types = [Types.STATE]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class DELUDED(CardInfo):
    names = ["Deluded", "Deludeds", "Deluded"]
    types = [Types.STATE]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class LOST_IN_THE_WOODS(CardInfo):
    names = ["Lost In The Woods", "Lost In The Woods", "Lost In The Woods"]
    types = [Types.STATE]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class BARD(CardInfo):
    names = ["Bard", "Bards", "a Bard"]
    types = [Types.ACTION, Types.FATE]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class BLESSED_VILLAGE(CardInfo):
    names = ["Blessed Village", "Blessed Villages", "a Blessed Village"]
    types = [Types.ACTION, Types.FATE]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CHANGELING(CardInfo):
    names = ["Changeling", "Changelings", "a Changeling"]
    types = [Types.NIGHT]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CEMETERY(CardInfo):
    names = ["Cemetery", "Cemeteries", "a Cemetery"]
    types = [Types.VICTORY]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class COBBLER(CardInfo):
    names = ["Cobbler", "Cobblers", "a Cobbler"]
    types = [Types.NIGHT, Types.DURATION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CONCLAVE(CardInfo):
    names = ["Conclave", "Conclaves", "a Conclave"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CRYPT(CardInfo):
    names = ["Crypt", "Crypts", "a Crypt"]
    types = [Types.NIGHT, Types.DURATION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CURSED_VILLAGE(CardInfo):
    names = ["Cursed Village", "Cursed Villages", "a Cursed Village"]
    types = [Types.ACTION, Types.DOOM]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class DEN_OF_SIN(CardInfo):
    names = ["Den of Sin", "Dens of Sin", "a Den of Sin"]
    types = [Types.NIGHT, Types.DURATION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class DEVILS_WORKSHOP(CardInfo):
    names = ["Devil's Workshop", "Devil's Workshops", "a Devil's Workshop"]
    types = [Types.NIGHT]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class DRUID(CardInfo):
    names = ["Druid", "Druids", "a Druid"]
    types = [Types.ACTION, Types.FATE]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class EXORCIST(CardInfo):
    names = ["Exorcist", "Exorcists", "an Exorcist"]
    types = [Types.NIGHT]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class FAITHFUL_HOUND(CardInfo):
    names = ["Faithful Hound", "Faithful Hounds", "a Faithful Hound"]
    types = [Types.ACTION, Types.REACTION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class FOOL(CardInfo):
    names = ["Fool", "Fools", "a Fool"]
    types = [Types.ACTION, Types.FATE]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class GHOST_TOWN(CardInfo):
    names = ["Ghost Town", "Ghost Towns", "a Ghost Town"]
    types = [Types.NIGHT, Types.DURATION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class GUARDIAN(CardInfo):
    names = ["Guardian", "Guardians", "a Guardian"]
    types = [Types.NIGHT, Types.DURATION]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class IDOL(CardInfo):
    names = ["Idol", "Idols", "an Idol"]
    types = [Types.TREASURE, Types.ATTACK, Types.FATE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class LEPRECHAUN(CardInfo):
    names = ["Leprechaun", "Leprechauns", "a Leprechaun"]
    types = [Types.ACTION, Types.DOOM]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class MONASTERY(CardInfo):
    names = ["Monastery", "Monasteries", "a Monastery"]
    types = [Types.NIGHT]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class NECROMANCER(CardInfo):
    names = ["Necromancer", "Necromancers", "a Necromancer"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class NIGHT_WATCHMAN(CardInfo):
    names = ["Night Watchman", "Night Watchmen", "a Night Watchman"]
    types = [Types.NIGHT]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class PIXIE(CardInfo):
    names = ["Pixie", "Pixies", "a Pixie"]
    types = [Types.ACTION, Types.FATE]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class POOKA(CardInfo):
    names = ["Pooka", "Pookas", "a Pooka"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class RAIDER(CardInfo):
    names = ["Raider", "Raiders", "a Raider"]
    types = [Types.NIGHT, Types.DURATION, Types.ATTACK]
    cost = [6, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SACRED_GROVE(CardInfo):
    names = ["Sacred Grove", "Sacred Groves", "a Sacred Grove"]
    types = [Types.ACTION, Types.FATE]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SECRET_CAVE(CardInfo):
    names = ["Secret Cave", "Secret Caves", "a Secret Cave"]
    types = [Types.ACTION, Types.DURATION]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SHEPHERD(CardInfo):
    names = ["Shepherd", "Shepherds", "a Shepherd"]
    types = [Types.ACTION]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class SKULK(CardInfo):
    names = ["Skulk", "Skulks", "a Skulk"]
    types = [Types.ACTION, Types.ATTACK, Types.DOOM]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TORMENTOR(CardInfo):
    names = ["Tormentor", "Tormentors", "a Tormentor"]
    types = [Types.ACTION, Types.ATTACK, Types.DOOM]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TRAGIC_HERO(CardInfo):
    names = ["Tragic Hero", "Tragic Heroes", "a Tragic Hero"]
    types = [Types.ACTION]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class TRACKER(CardInfo):
    names = ["Tracker", "Trackers", "a Tracker"]
    types = [Types.ACTION, Types.FATE]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class VAMPIRE(CardInfo):
    names = ["Vampire", "Vampires", "a Vampire"]
    types = [Types.NIGHT, Types.ATTACK, Types.DOOM]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WEREWOLF(CardInfo):
    names = ["Werewolf", "Werewolves", "a Werewolf"]
    types = [Types.ACTION, Types.NIGHT, Types.ATTACK, Types.DOOM]
    cost = [5, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class CURSED_GOLD(CardInfo):
    names = ["Cursed Gold", "Cursed Golds", "a Cursed Gold"]
    types = [Types.TREASURE, Types.HEIRLOOM]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class GOAT(CardInfo):
    names = ["Goat", "Goats", "a Goat"]
    types = [Types.TREASURE, Types.HEIRLOOM]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class HAUNTED_MIRROR(CardInfo):
    names = ["Haunted Mirror", "Haunted Mirrors", "a Haunted Mirror"]
    types = [Types.TREASURE, Types.HEIRLOOM]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class LUCKY_COIN(CardInfo):
    names = ["Lucky Coin", "Lucky Coins", "a Lucky Coin"]
    types = [Types.TREASURE, Types.HEIRLOOM]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class MAGIC_LAMP(CardInfo):
    names = ["Magic Lamp", "Magic Lamps", "a Magic Lamp"]
    types = [Types.TREASURE, Types.HEIRLOOM]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class PASTURE(CardInfo):
    names = ["Pasture", "Pastures", "a Pasture"]
    types = [Types.TREASURE, Types.VICTORY, Types.HEIRLOOM]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class POUCH(CardInfo):
    names = ["Pouch", "Pouches", "a Pouch"]
    types = [Types.TREASURE, Types.HEIRLOOM]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class BAT(CardInfo):
    names = ["Bat", "Bats", "a Bat"]
    types = [Types.NIGHT]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class GHOST(CardInfo):
    names = ["Ghost", "Ghosts", "a Ghost"]
    types = [Types.NIGHT, Types.DURATION, Types.SPIRIT]
    cost = [4, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class IMP(CardInfo):
    names = ["Imp", "Imps", "an Imp"]
    types = [Types.ACTION, Types.SPIRIT]
    cost = [2, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WILL_O_WISP(CardInfo):
    names = ["Will-o'-Wisp", "Will-o'-Wisps", "a Will-o'-Wisp"]
    types = [Types.ACTION, Types.SPIRIT]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class WISH(CardInfo):
    names = ["Wish", "Wishes", "a Wish"]
    types = [Types.ACTION]
    cost = [0, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class ZOMBIE_APPRENTICE(CardInfo):
    names = ["Zombie Apprentice", "Zombie Apprentices", "a Zombie Apprentice"]
    types = [Types.ACTION, Types.ZOMBIE]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class ZOMBIE_MASON(CardInfo):
    names = ["Zombie Mason", "Zombie Masons", "a Zombie Mason"]
    types = [Types.ACTION, Types.ZOMBIE]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state


class ZOMBIE_SPY(CardInfo):
    names = ["Zombie Spy", "Zombie Spies", "a Zombie Spy"]
    types = [Types.ACTION, Types.ZOMBIE]
    cost = [3, 0, 0]

    def onPlay(self, state, log, cardIndex):
        state = deepcopy(state)
        state.stack += []
        state.candidates = state.stack.pop()
        return state
