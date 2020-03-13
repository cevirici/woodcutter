from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt

from random import randint
from .src import *
from .models import *
import re


def index(request):
    return HttpResponse("Test.")


def inputFields(request):
    return render(request, 'woodcutter/inputform.html')


def main(request):
    logCount = len(GameLog.objects.all())
    return render(request, 'woodcutter/main.html', {'logcount': logCount})


def logSearch(request):
    return render(request, 'woodcutter/logsearch.html')


def random(request):
    logs = GameLog.objects.filter(valid=True)
    i = randint(0, len(logs) - 1)
    gameIndex = logs[i].game_id
    return HttpResponseRedirect(reverse('woodcutter:display',
                                        args=(gameIndex,)))


@csrf_exempt
def submit(request):
    if int(request.POST['v']) < 3:
        # Invalid version of grabber
        return request.POST['v']

    version = int(request.POST['v'])
    gameId, players = parse_header(request.POST['header'])
    combinedLog = combined_parse(request.POST['logs'])
    supply = request.POST['supply']

    try:
        oldLog = GameLog.objects.get(game_id=gameId)
    except ObjectDoesNotExist:
        GameLog.objects.create(version=version,
                               game_id=gameId,
                               log=combinedLog,
                               supply=supply,
                               players=players)
    else:
        oldLog.version = 2
        oldLog.log = combinedLog
        oldLog.supply = supply
        oldLog.players = players
        oldLog.save()

    # Try to parse
    # log = get_object_or_404(GameLog, game_id=gameID)
    # players = log.players.split('~')

    # parsedLog, supply = unpack(log.log, log.supply)
    # blockLengths = get_blocklengths(parsedLog)
    # try:
    #     gameStates = parse_everything(parsedLog, blockLengths, supply)
    # except BaseException:
    #     log.valid = False
    #     log.save()
    #     raise
    # log.valid = gameStates[-1].valid
    # log.save()

    return HttpResponseRedirect(reverse('woodcutter:display', args=(gameId,)))


def dump(request, game_id):
    log = get_object_or_404(GameLog, game_id=game_id)
    states = simulate(log)
    return HttpResponse('<br>'.join([repr(s.move) + ", " + str(s.coins) for s in states]))


def plaintext(request, game_id):
    log = get_object_or_404(GameLog, game_id=game_id)
    cards, preds = getInfo(log.version)

    printer = Printer(log.version)
    printedLog = [printer.print_line(line) for line in log.log.split("~")]
    return HttpResponse(printer.print_supply(log.supply) + '<br>' +
                        '<br>'.join(printedLog))


def detailed(request, game_id):
    log = get_object_or_404(GameLog, game_id=game_id)
    players = log.players.split('~')

    parsedLog, supply = unpack(log.log, log.supply)
    blockLengths = get_blocklengths(parsedLog)
    try:
        gameStates = parse_everything(parsedLog, blockLengths, supply)
    except BaseException:
        log.valid = False
        log.save()
        raise
    log.valid = gameStates[-1].valid
    log.save()
    story = elaborate_story(players, parsedLog)

    output = []
    i = 0
    for line, state in zip(story, gameStates[1:]):
        output.append('Decision {}'.format(str(i)))
        output.append(line + '<br>' + str(state))
        i += 1
    return HttpResponse('<br>'.join(output))


def display(request, game_id, logIndex=0):
    log = get_object_or_404(GameLog, game_id=game_id)
    players = log.players.split('~')
    players = ['UNKNOWN PLAYER' if x == '' else x for x in players]

    gameMoves, supply = unpack(log.log, log.supply)
    blockLengths = get_blocklengths(gameMoves)
    try:
        gameStates = parse_everything(gameMoves, blockLengths, supply)
    except BaseException:
        log.valid = False
        log.save()
        raise
    log.valid = gameStates[-1].valid
    log.save()

    titleString = 'Game {}: {} vs. {}'.format(str(game_id), *players)
    colors, borders, urls = get_passables()
    kingdomRaw, pairs = get_kingdom(supply)
    pairStr = '~'.join(['|'.join([str(Cards[card].index)
                                  for card in [pairs[cards]] + list(cards)])
                        for cards in pairs])
    scores = [get_vps(state, kingdomRaw[3]) for state in gameStates]

    stepPoints, turnPoints = get_points(gameMoves)
    kingdomStr = [[str(Cards[card].index) for card in row]
                  for row in kingdomRaw]
    turnStates = [gameStates[i] for i in turnPoints]
    turnDecks = ['/'.join([repr(state.crunch(GameState.playerZones, [player]))
                           for player in range(2)]) for state in turnStates]

    context = {'logIndex': logIndex,
               'kingdom': '~'.join(['|'.join(x) for x in kingdomStr]),
               'pairs': pairStr,
               'story': '~'.join(elaborate_story(players, gameMoves, True)),
               'boards': '~'.join([repr(x) for x in gameStates]),
               'titlestring': titleString,
               'players': players,
               'turnOwners': get_turn_owners(gameStates),
               'stepPoints': stepPoints,
               'turnPoints': turnPoints,
               'interiors': colors,
               'borders': borders,
               'urls': urls,
               'phases': ''.join([str(x) for x in get_phases(gameStates)]),
               'inplays': '~'.join(get_inplays(gameStates)),
               'scores': '~'.join([' '.join(scores[point][0])
                                   for point in turnPoints]),
               'scoreTotals': '~'.join(['|'.join(score[1])
                                        for score in scores]),
               'costs': '~'.join([str(sum(card.cost)) for card in CardList]),
               'turnDecks': '~'.join(turnDecks)}

    return render(request, 'woodcutter/display.html', context)


def error_list(request):
    rawLogs = GameLog.objects.filter(valid=False).all()
    errorLogs = []
    for rawLog in rawLogs:
        players = rawLog.players.split('~')
        title = 'Game #{}: {} - {}'.format(rawLog.game_id, *players)

        errorLogs.append([title, rawLog.game_id])

    context = {
        'error_logs': errorLogs
    }
    return render(request, 'woodcutter/errorList.html', context)


@csrf_exempt
def find_logs(request):
    def clean(inString):
        return re.sub(',|-| |\'', '', inString).lower()

    cleanNames = [clean(cardName) for cardName in standardNames]

    searchCards = request.POST['cards'].split(',')
    searchCardIndices = [cleanNames.index(clean(cardName)) for cardName in
                         searchCards if clean(cardName) in cleanNames]

    optionalCards = request.POST['optionals'].split(',')
    optionalCardIndices = [cleanNames.index(clean(cardName)) for cardName in
                           optionalCards if clean(cardName) in cleanNames]

    errors = request.POST['errors']

    players = []
    if len(request.POST['players']) > 0:
        players = request.POST['players'].split(',')
    rawLogs = GameLog.objects.all()

    def matchLog(rawLog, search, optional, players, errors):
        rawLogCards = rawLog.supply.split('~')
        logCards = [int(card[:3], 16) for card in rawLogCards]
        for card in searchCardIndices:
            if card not in logCards:
                return False

        if len([card for card in optionalCardIndices if card in logCards]) \
                < min(len(optionalCardIndices), 1):
            return False

        logPlayers = rawLog.players.split('~')
        if len([player for player in players if player in logPlayers]) \
                < min(len(players), 1):
            return False

        if (errors == "0" and not rawLog.valid) or \
           (errors == "2" and rawLog.valid):
            return False

        return True

    outputLogs = ['<a href = "{}/display">{}</a>'.format(rawLog.game_id, rawLog.game_id)
                  for rawLog in rawLogs if matchLog(rawLog, searchCards,
                  optionalCards, players, errors)]

    for i in range(5, len(outputLogs), 5):
        outputLogs[i] = '<br>' + outputLogs[i]
    outputLogString = ','.join(outputLogs)
    return HttpResponse(outputLogString)


def error_404(request):
    data = {}
    return render(request, 'woodcutter/error_404.html', data)


def error_500(request):
    data = {}
    return render(request, 'woodcutter/error_500.html', data)
