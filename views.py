from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt

from random import randint
from .src import *
from .models import GameLog
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
    logs = GameLog.objects.all()
    i = randint(0, len(logs) - 1)
    gameIndex = logs[i].game_id
    return HttpResponseRedirect(reverse('woodcutter:display',
                                        args=(gameIndex,)))


@csrf_exempt
def submit(request):
    condensedLog, gameID = combined_parse([request.POST['fileone'],
                                           request.POST['filetwo']])
    supply = parse_supply(request.POST['supply'])
    players = request.POST['players']

    try:
        oldLog = GameLog.objects.get(game_id=gameID)
    except ObjectDoesNotExist:
        GameLog.objects.create(game_id=gameID,
                               log=condensedLog,
                               supply=supply,
                               players=players)
    else:
        oldLog.log = condensedLog
        oldLog.supply = supply
        oldLog.players = players
        oldLog.save()

    return HttpResponseRedirect(reverse('woodcutter:display', args=(gameID,)))


def plaintext(request, game_id):
    log = get_object_or_404(GameLog, game_id=game_id)
    players = log.players.split('~')

    parsedLog, supply = unpack(log.log, log.supply)
    gameMoves, blockLengths = parse_gameLog(parsedLog)
    try:
        gameStates = parse_everything(gameMoves, blockLengths, supply)
    except BaseException:
        log.valid = False
        log.save()
        raise

    log.valid = gameStates[-1]['VALID']
    log.save()

    turnPoints = get_turn_points(blockLengths)
    story, storyPlain = elaborate_story(players, gameMoves, turnPoints)
    return HttpResponse('<br>'.join(storyPlain))


def display(request, game_id):
    log = get_object_or_404(GameLog, game_id=game_id)
    players = log.players.split('~')

    (parsedLog, supply) = unpack(log.log, log.supply)
    (gameMoves, blockLengths) = parse_gameLog(parsedLog)
    try:
        gameStates = parse_everything(gameMoves, blockLengths, supply)
    except BaseException:
        log.valid = False
        log.save()
        raise

    log.valid = gameStates[-1]['VALID']
    log.save()

    turnPoints = get_turn_points(blockLengths)
    turnOwners = get_turn_owners(gameMoves, turnPoints)
    shuffledTurns = get_shuffled_turns(gameMoves, turnPoints)

    involvedCards = get_involved_cards(gameStates)

    allCards = find_turn_decks(turnPoints, gameStates)
    gainedCards = find_gained_cards(turnPoints, gameStates)

    cleanupPoints = [x+y for x, y in zip(get_cleanup_points(gameMoves),
                     [-1] + turnPoints)]
    cleanupPoints[0] = turnPoints[0] + 1
    progressCards = find_shuffle_progress(turnPoints, cleanupPoints,
                                          gameStates)

    vpCards = find_vp(turnPoints, gameStates, gameData[1])

    graph_all_top = render_graph_row(allCards, [''], 0)
    graph_all_bot = render_graph_row(allCards, [''], 1)

    graph_gained_top = render_graph_row(gainedCards, ['redoutline', 'redoutline faded', ''], 0)
    graph_gained_bot = render_graph_row(gainedCards, ['redoutline', 'redoutline faded', ''], 1)

    graph_progress_top = render_graph_row(progressCards, ['faded', '', 'faded'], 0)
    graph_progress_bot = render_graph_row(progressCards, ['faded', '', 'faded'], 1)

    graph_vps_top = render_vp_row(vpCards, 0)
    graph_vps_bot = render_vp_row(vpCards, 1)

    axisLabels = render_axis_labels(turnOwners)
    bgData_top = render_graph_background(turnOwners, shuffledTurns, 0)
    bgData_bot = render_graph_background(turnOwners, shuffledTurns, 1)
    legendBoxes = render_legend_boxes(involvedCards)
    sidebarLabels = render_story_sidebar_labels(turnOwners, turnPoints)
    storyRaw = elaborate_story(players, gameMoves)
    story = storyRaw[0]
    storyPlain = storyRaw[1]

    full_printout(gameMoves, gameStates)

    kingdom = render_kingdom(gameData[1])

    titleString = 'Game #{}: {} - {}'.format(game_id, players[0], players[1])
    kingdomColors = relevantColors(gameData[1])

    cards = [x.simple_name for x in standardCards]

    context = {
        'title_string': titleString,
        'gameStates': exportGameStates(gameStates),
        'relevantColors': kingdomColors,
        'graph_all_top': graph_all_top,
        'graph_all_bot': graph_all_bot,
        'graph_gained_top': graph_gained_top,
        'graph_gained_bot': graph_gained_bot,
        'graph_progress_top': graph_progress_top,
        'graph_progress_bot': graph_progress_bot,
        'graph_vps_top': graph_vps_top[0],
        'graph_vps_labels_top': graph_vps_top[1],
        'graph_vps_bot': graph_vps_bot[0],
        'graph_vps_labels_bot': graph_vps_bot[1],
        'turnOwners': turnOwners,
        'bgData_top': bgData_top,
        'bgData_bot': bgData_bot,
        'axisLabels': axisLabels,
        'legendBoxes': legendBoxes,
        'story_lines': story,
        'sidebar_labels': sidebarLabels,
        'kingdomCards': kingdom,
        'storyPlain': storyPlain,
        'gameid': game_id,
    }

    return render(request, 'woodcutter/display.html', context)


def quickUpdate(request):
    game_ids = request.GET['ids'].split(',')[:50]
    for game_id in game_ids:
        log = get_object_or_404(GameLog, game_id=game_id)
        players = log.players.split('~')

        repairable = True
        while repairable:
            moveData = unpack(log.log, log.supply)
            indents = [parsedLine.indent for parsedLine in moveData[0]]
            moveTree = parse_game(moveData[0])
            try:
                gameStates = get_decision_state(moveTree, moveData[1])
            except BaseException:
                log.valid = False
                log.save()
                raise

            attemptedRepair = fullRepair(log.log, moveTree, gameStates, moveData[1])
            if attemptedRepair[1]:
                log.log = attemptedRepair[0]
                log.save()
            else:
                repairable = False

        log.valid = gameStates[-1].valid
        log.save()

    return render(request, 'woodcutter/main.html')


def error_list(request):
    rawLogs = GameLog.objects.filter(valid=False).all()
    errorLogs = []
    for rawLog in rawLogs:
        players = rawLog.players.split('~')
        title = 'Game #{}: {} - {}'.format(rawLog.game_id, players[0], players[1])

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


@csrf_exempt
def edit_log(request):
    gameid = request.POST['gameid']
    lineNumber = int(request.POST['lineNumber'])
    rawinput = request.POST['input']

    log = get_object_or_404(GameLog, game_id=gameid)
    logStrings = log.log.split('~')
    players = log.players.split('~')

    newIndent = len(re.match('^>*', rawinput).group(0))
    rawinput = rawinput[newIndent:]
    newLine = parse_line_contents(rawinput)
    newLine.indent = newIndent
    newLine.pred = standardPreds.index(newLine.pred)
    newLine.player = players.index(newLine.player)
    returnData = '~'.join(elaborate_line(players, newLine))
    returnData += '~{}'.format(newLine.indent)

    newLine.pred = '{:0>2}'.format(hex(newLine.pred)[2:])
    newLine.player = hex(newLine.player + 1)[2:]

    logStrings[lineNumber] = str(newLine)

    log.log = '~'.join(logStrings)
    log.save()
    return HttpResponse(returnData)


def error_404(request):
    data = {}
    return render(request, 'woodcutter/error_404.html', data)


def error_500(request):
    data = {}
    return render(request, 'woodcutter/error_500.html', data)
