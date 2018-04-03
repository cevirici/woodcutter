from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from .src import *
from .models import GameLog


def index(request):
    return HttpResponse("Test.")


def inputFields(request):
    return render(request, 'woodcutter/inputform.html')


def main(request):
    return render(request, 'woodcutter/main.html')


@csrf_exempt
def submit(request):
    arr = [request.POST['fileone'], request.POST['filetwo']]
    ret = combined_parse(arr)
    sup = parse_supply(request.POST['supply'])
    players = request.POST['players']

    gameid = ret[1]
    try:
        existinglog = GameLog.objects.get(game_id=gameid)
    except ObjectDoesNotExist:
        newLog = GameLog.objects.create(game_id=ret[1],
                                        log=ret[0],
                                        supply=sup,
                                        players=players)
    # else:
        # existinglog.log = ret[0]
        # existinglog.supply = sup
        # existinglog.players = players
        # existinglog.save()

    return HttpResponseRedirect(reverse('woodcutter:display', args=(ret[1],)))


def display(request, game_id):
    log = get_object_or_404(GameLog, game_id=game_id)

    moveData = unpack(log.log, log.supply)
    indents = [parsedLine.indent for parsedLine in moveData[0]]
    players = log.players.split('~')

    moveTree = parse_game(moveData[0])
    try:
        gameStates = get_decision_state(moveTree, moveData[1])
    except BaseException:
        log.valid = False
        log.save()
        raise

    log.valid = gameStates[-1].valid
    log.save()

    turnPoints = get_turn_points(moveTree)
    turnOwners = get_turn_owners(moveTree)
    shuffledTurns = get_shuffled_turns(moveTree)

    involvedCards = get_involved_cards(gameStates)

    allCards = find_turn_decks(turnPoints, gameStates)
    gainedCards = find_gained_cards(turnPoints, gameStates)

    cleanupPoints = [x+y for x, y in zip(get_cleanup_points(moveTree),
                     [-1] + turnPoints)]
    cleanupPoints[0] = turnPoints[0] + 1
    progressCards = find_shuffle_progress(turnPoints, cleanupPoints,
                                          gameStates)

    vpCards = find_vp(turnPoints, gameStates)

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
    storyRaw = elaborate_story(players, moveTree)
    story = storyRaw[0]
    storyPlain = storyRaw[1]

    full_printout(moveTree, gameStates)

    kingdom = render_kingdom(moveData[1])

    titleString = 'Game #{}: {} - {}'.format(game_id, players[0], players[1])
    kingdomColors = relevantColors(moveData[1])

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


def error_list(request):
    for log in GameLog.objects.all():
        moveData = unpack(log.log, log.supply)
        players = log.players.split('~')

        moveTree = parse_game(moveData[0])
        try:
            gameStates = get_decision_state(moveTree, moveData[1])
        except BaseException:
            log.valid = False
            log.save()

        log.valid = gameStates[-1].valid
        log.save()

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


def error_404(request):
    data = {}
    return render(request, 'woodcutter/error_404.html', data)


def error_500(request):
    data = {}
    return render(request, 'woodcutter/error_500.html', data)


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
