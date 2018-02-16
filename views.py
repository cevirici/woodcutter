from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from .src import Parser, Renderer, unpack
from .models import GameLog, CardData, PredData, ExceptionData

def index(request):
    return HttpResponse("Test.")

def inputFields(request):
	return render(request,'woodcutter/inputform.html')

@csrf_exempt
def submit(request):
	preds = PredData.objects.all()
	cards = CardData.objects.all()

	p = Parser(preds,cards)
	arr = [request.POST['fileone'],request.POST['filetwo']]
	ret = p.combined_parse(arr)
	sup = p.parse_supply(request.POST['supply'])
	players = request.POST['players']

	gameid = ret[1]
	try:
		existinglog = GameLog.objects.get(game_id=gameid)
	except ObjectDoesNotExist:
		newLog = GameLog.objects.create(game_id=ret[1],log=ret[0],supply=sup,players=players)
	else:
		existinglog.log = ret[0]
		existinglog.supply = sup
		existinglog.players=players
		existinglog.save()

	return HttpResponseRedirect(reverse('woodcutter:display', args=(ret[1],)))

def display(request,game_id):
	preds = PredData.objects.all()
	cards = CardData.objects.all()
	r = Renderer(preds,cards)

	log = get_object_or_404(GameLog, game_id=game_id)

	moveData = unpack(log.log,log.supply)

	decisionLog = r.parse_game(moveData[0],moveData[1],2) #Change playercount when you want to later on
	turnData = r.get_turn_data(decisionLog[1],decisionLog[2], len(decisionLog[0]))
	involvedCards = r.get_involved_cards(decisionLog[0])

	bg_top_row = r.render_graph_bg_row(turnData[1],turnData[2][0],0)
	bg_bot_row = r.render_graph_bg_row(turnData[1],turnData[2][1],1)
	bg_axis = r.render_graph_axis(turnData[1])

	legend = r.render_legend(involvedCards)

	turn_decks = r.find_turn_decks(decisionLog[0],turnData[0],turnData[1])
	graph_all_top = r.render_graph_row(turn_decks[0],0)
	graph_all_bot = r.render_graph_row(turn_decks[1],1)

	turn_gained = r.find_gained_cards(decisionLog[0],turnData[0],turnData[1])
	graph_gained_top = r.render_graph_row(turn_gained[0],0)
	graph_gained_bot = r.render_graph_row(turn_gained[1],1)

	turn_shuffle = r.find_full(decisionLog[0],turnData[0],turnData[1])
	graph_shuffle_top = r.render_graph_row(turn_shuffle[0],0)
	graph_shuffle_bot = r.render_graph_row(turn_shuffle[1],1)

	story_main = r.render_story_main(r.elaborate_story(log.players.split('~'),moveData[0]),turnData[0])
	story_sidebar = r.render_story_sidebar(turnData[1],turnData[0])

	context = {
		'graph_all_toprow': graph_all_top,
		'graph_all_botrow': graph_all_bot,
		'graph_gained_toprow': graph_gained_top,
		'graph_gained_botrow': graph_gained_bot,
		'graph_shuffle_toprow': graph_shuffle_top,
		'graph_shuffle_botrow': graph_shuffle_bot,
		'graph_bg_top': bg_top_row,
		'graph_bg_bot': bg_bot_row,
		'graph_bg_axis': bg_axis,
		'legend': legend,
		'story_main': story_main,
		'story_sidebar': story_sidebar,
	}

	return render(request,'woodcutter/display.html', context)