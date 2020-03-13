from .Enums import *
from .Card import *
from copy import deepcopy
from .GenericActions import *


class CardInfo:
    names = ["Back", "Backs", "a Back"]
    types = []

    def hasType(self, cardType):
        return cardType in self.types


class CURSE(CardInfo):
    names = ["Curse", "Curses", "a Curse"]
    types = [Types.CURSE]


class COPPER(CardInfo):
    names = ["Copper", "Coppers", "a Copper"]
    types = [Types.TREASURE]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.candidates = [state.stack.pop()]
        state.coins += 1
        return state


class SILVER(CardInfo):
    names = ["Silver", "Silvers", "a Silver"]
    types = [Types.TREASURE]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.candidates = [state.stack.pop()]
        state.coins += 2
        return state


class GOLD(CardInfo):
    names = ["Gold", "Golds", "a Gold"]
    types = [Types.TREASURE]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.candidates = [state.stack.pop()]
        state.coins += 3
        return state


class ESTATE(CardInfo):
    names = ["Estate", "Estates", "an Estate"]
    types = [Types.VICTORY]


class DUCHY(CardInfo):
    names = ["Duchy", "Duchies", "a Duchy"]
    types = [Types.VICTORY]


class PROVINCE(CardInfo):
    names = ["Province", "Provinces", "a Province"]
    types = [Types.VICTORY]


class ARTISAN(CardInfo):
    names = ["Artisan", "Artisans", "an Artisan"]
    types = [Types.ACTION]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [topdeck(),
                        maybe(gain(NeutralZones.SUPPLY, PlayerZones.HAND))]
        state.candidates = [state.stack.pop()]
        return state


class BANDIT(CardInfo):
    names = ["Bandit", "Bandits", "a Bandit"]
    types = [Types.ACTION, Types.ATTACK]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [maybe(discard(PlayerZones.DECK, PlayerZones.DISCARD)),
                        maybe(trash(PlayerZones.DECK, NeutralZones.TRASH)),
                        maybe(revealN(2)),
                        maybe(gain()),
                        reactToAttack()]
        state.candidates = [state.stack.pop()]
        return state


class BUREAUCRAT(CardInfo):
    names = ["Bureaucrat", "Bureaucrats", "a Bureaucrat"]
    types = [Types.ACTION, Types.ATTACK]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [maybe(topdeck()),
                        maybe(revealHand()),
                        maybe(gain(NeutralZones.SUPPLY, PlayerZones.DECK)),
                        reactToAttack()]
        state.candidates = [state.stack.pop()]
        return state


class CELLAR(CardInfo):
    names = ["Cellar", "Cellars", "a Cellar"]
    types = [Types.ACTION]

    def onPlay(self, state, log):
        state = deepcopy(state)
        if state.logLine < len(log) - 1:
            amount = len(log[state.logLine + 1].items)
        state.stack += [maybe(drawN(amount)),
                        maybe(discard()),
                        getAction()]
        state.candidates = [state.stack.pop()]
        return state


class CHAPEL(CardInfo):
    names = ["Chapel", "Chapels", "a Chapel"]
    types = [Types.ACTION]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [maybe(trash())]
        state.candidates = [state.stack.pop()]
        return state


class COUNCIL_ROOM(CardInfo):
    names = ["Council Room", "Council Rooms", "a Council Room"]
    types = [Types.ACTION]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [drawN(1), getBuy(), drawN(4)]
        state.candidates = [state.stack.pop()]
        return state


class FESTIVAL(CardInfo):
    names = ["Festival", "Festivals", "a Festival"]
    types = [Types.ACTION]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [getCoin(), getBuy(), getAction()]
        state.candidates = [state.stack.pop()]
        return state


class GARDENS(CardInfo):
    names = ["Gardens", "Gardens", "a Gardens"]
    types = [Types.VICTORY]


class HARBINGER(CardInfo):
    names = ["Harbinger", "Harbingers", "a Harbinger"]
    types = [Types.ACTION]

    def onPlay(self, state, log):
        state = deepcopy(state)
        # For some reason harbinger looks at discard twice
        state.stack += [maybe(topdeck(PlayerZones.DISCARD, PlayerZones.DECK)),
                        maybe(lookAt()), maybe(lookAt()),
                        getAction(), drawN(1)]
        state.candidates = [state.stack.pop()]
        return state


class LABORATORY(CardInfo):
    names = ["Laboratory", "Laboratories", "a Laboratory"]
    types = [Types.ACTION]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [getAction(), drawN(2)]
        state.candidates = [state.stack.pop()]
        return state


class LIBRARY(CardInfo):
    names = ["Library", "Libraries", "a Library"]
    types = [Types.ACTION]

    def onPlay(self, state, log):
        state = deepcopy(state)
        logLine = log[state.logLine]
        state.player = logLine.player

        handCount = state.zoneCount(PlayerZones.HAND)
        deckCount = state.zoneCount(PlayerZones.DECK) + \
            state.zoneCount(PlayerZones.DISCARD)

        if handCount >= 7 or deckCount == 0:
            state.candidates = [maybe(discard(PlayerZones.SET_ASIDE,
                                              PlayerZones.DISCARD))]
        else:
            state.stack += [onPlay("Library"), maybe(setAside()),
                            maybe(lookAt()), drawN(1)]
            state.candidates = [state.stack.pop()]

        return state


class MARKET(CardInfo):
    names = ["Market", "Markets", "a Market"]
    types = [Types.ACTION]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [getCoin(), getBuy(), getAction(), drawN(1)]
        state.candidates = [state.stack.pop()]
        return state


class MERCHANT(CardInfo):
    names = ["Merchant", "Merchants", "a Merchant"]
    types = [Types.ACTION]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [getAction(), drawN(1)]
        state.candidates = [state.stack.pop()]
        return state


class MILITIA(CardInfo):
    names = ["Militia", "Militias", "a Militia"]
    types = [Types.ACTION, Types.ATTACK]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [maybe(discard()), getCoin(), reactToAttack()]
        state.candidates = [state.stack.pop()]
        return state


class MINE(CardInfo):
    names = ["Mine", "Mines", "a Mine"]
    types = [Types.ACTION]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [gain(NeutralZones.SUPPLY, PlayerZones.HAND),
                        trash()]
        state.candidates = [state.stack.pop()]
        return state


class MOAT(CardInfo):
    # The reaction aspect of moat is baked into every attack -
    # The 'attack' parts are all maybe-d.
    names = ["Moat", "Moats", "a Moat"]
    types = [Types.ACTION]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [drawN(2)]
        state.candidates = [state.stack.pop()]
        return state

    def onReact(self, state, log):
        state = deepcopy(state)
        state.candidates = [state.stack.pop()]
        return state


class MONEYLENDER(CardInfo):
    names = ["Moneylender", "Moneylenders", "a Moneylender"]
    types = [Types.ACTION]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [maybe(getCoin()), maybe(trash())]
        state.candidates = [state.stack.pop()]
        return state


class POACHER(CardInfo):
    names = ["Poacher", "Poachers", "a Poacher"]
    types = [Types.ACTION]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [maybe(discard()), getCoin(), getAction(), drawN(1)]
        state.candidates = [state.stack.pop()]
        return state


class REMODEL(CardInfo):
    names = ["Remodel", "Remodels", "a Remodel"]
    types = [Types.ACTION]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [gain(), trash()]
        state.candidates = [state.stack.pop()]
        return state


class SENTRY(CardInfo):
    names = ["Sentry", "Sentries", "a Sentry"]
    types = [Types.ACTION]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [maybe(topdeck(PlayerZones.DECK, PlayerZones.DECK)),
                        maybe(discard(PlayerZones.DECK, PlayerZones.DECK)),
                        maybe(trash(PlayerZones.DECK, PlayerZones.DECK)),
                        maybe(lookAt()), getAction(), drawN(1)]
        state.candidates = [state.stack.pop()]
        return state


class SMITHY(CardInfo):
    names = ["Smithy", "Smithies", "a Smithy"]
    types = [Types.ACTION]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [drawN(3)]
        state.candidates = [state.stack.pop()]
        return state


class THRONE_ROOM(CardInfo):
    names = ["Throne Room", "Throne Rooms", "a Throne Room"]
    types = [Types.ACTION]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [replay(), play()]
        state.candidates = [state.stack.pop()]
        return state


class VASSAL(CardInfo):
    names = ["Vassal", "Vassals", "a Vassal"]
    types = [Types.ACTION]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [maybe(play(PlayerZones.DISCARD)),
                        maybe(discard(PlayerZones.DECK, PlayerZones.DISCARD)),
                        getCoin()]
        state.candidates = [state.stack.pop()]
        return state


class VILLAGE(CardInfo):
    names = ["Village", "Villages", "a Village"]
    types = [Types.ACTION]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [getAction(), drawN(1)]
        state.candidates = [state.stack.pop()]
        return state


class WITCH(CardInfo):
    names = ["Witch", "Witches", "a Witch"]
    types = [Types.ACTION, Types.ATTACK]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [maybe(gain()), drawN(2), reactToAttack()]
        state.candidates = [state.stack.pop()]
        return state


class WORKSHOP(CardInfo):
    names = ["Workshop", "Workshops", "a Workshop"]
    types = [Types.ACTION]

    def onPlay(self, state, log):
        state = deepcopy(state)
        state.stack += [maybe(gain())]
        state.candidates = [state.stack.pop()]
        return state


def getCardInfo(card):
    correspondences = {
        "Curse": CURSE,
        "Copper": COPPER,
        "Silver": SILVER,
        "Gold": GOLD,
        "Estate": ESTATE,
        "Duchy": DUCHY,
        "Province": PROVINCE,
        "Artisan": ARTISAN,
        "Bandit": BANDIT,
        "Bureaucrat": BUREAUCRAT,
        "Cellar": CELLAR,
        "Chapel": CHAPEL,
        "Council Room": COUNCIL_ROOM,
        "Festival": FESTIVAL,
        "Gardens": GARDENS,
        "Harbinger": HARBINGER,
        "Laboratory": LABORATORY,
        "Library": LIBRARY,
        "Market": MARKET,
        "Merchant": MERCHANT,
        "Militia": MILITIA,
        "Mine": MINE,
        "Moat": MOAT,
        "Moneylender": MONEYLENDER,
        "Poacher": POACHER,
        "Remodel": REMODEL,
        "Sentry": SENTRY,
        "Smithy": SMITHY,
        "Throne Room": THRONE_ROOM,
        "Vassal": VASSAL,
        "Village": VILLAGE,
        "Witch": WITCH,
        "Workshop": WORKSHOP
    }
    if card in correspondences:
        return correspondences[card]()
    else:
        return CardInfo()
