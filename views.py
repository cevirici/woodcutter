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
    return render(request,'woodcutter/inputform.html')

def main(request):
    return render(request,'woodcutter/main.html')

@csrf_exempt
def submit(request):
    p = Parser()
    arr = [request.POST['fileone'],request.POST['filetwo']]
    ret = p.combined_parse(arr)
    sup = p.parse_supply(request.POST['supply'])
    players = request.POST['players']

    gameid = ret[1]
    try:
        existinglog = GameLog.objects.get(game_id=gameid)
    except ObjectDoesNotExist:
        newLog = GameLog.objects.create(game_id=ret[1],
                                        log=ret[0],
                                        supply=sup,
                                        players=players)
    else:
        existinglog.log = ret[0]
        existinglog.supply = sup
        existinglog.players = players
        existinglog.save()

    return HttpResponseRedirect(reverse('woodcutter:display', args=(ret[1],)))

def display(request, game_id):
    log = get_object_or_404(GameLog, game_id=game_id)

    moveData = unpack(log.log, log.supply)
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

    cleanupPoints = [x+y for x,y in zip(get_cleanup_points(moveTree), [-1] + turnPoints)]
    cleanupPoints[0] = turnPoints[0] + 1
    progressCards = find_shuffle_progress(turnPoints, cleanupPoints, gameStates)

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
    story = elaborate_story(players, moveTree)

    #DEBUG BLOCK
    full_printout(moveTree, gameStates)

    kingdom = render_kingdom(moveData[1])

    titleString = 'Game #{}: {} - {}'.format(game_id, players[0],players[1])

    context = {
        'title_string': titleString,
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
        'kingdomCards': kingdom
    }

    return render(request, 'woodcutter/display.html', context)

def error_list(request):
    rawLogs = GameLog.objects.filter(valid=False).all()
    errorLogs = []
    for rawLog in rawLogs:
        players = rawLog.players.split('~')
        title = 'Game #{}: {} - {}'.format(rawLog.game_id, players[0], players[1])

        errorLogs.append([title])

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
