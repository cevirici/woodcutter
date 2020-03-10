from woodcutter.models import *
from django.core.management.base import BaseCommand, CommandError
from django.shortcuts import get_object_or_404, render


def v0ToV1(game_id):
    log = get_object_or_404(GameLog, game_id=game_id)
    postRen = log.log[1] == '|'
    lines = log.log.split('~')

    def parseLine(line):
        if postRen:
            (indent, pred, player, items, args) = line.split('|')
            pred = str(int(pred, 16))

            items = items.replace('/', '+')
            if args:
                args = args.split('/')
            else:
                args = []
            if items:
                items = [x.split(':') for x in items.split('+')]
                trueItems = []
                for (c, i) in items:
                    card = int(i, 16)
                    if c == '255':
                        c = '1'
                    trueItems.append([c, str(card)])
                itemsStr = '+'.join([':'.join(x) for x in trueItems])
            else:
                itemsStr = ''

            args = '+'.join(args)

            return '|'.join([indent, pred, player, itemsStr, args])
        else:
            player = line[0:1]
            indent = line[1:2]
            pred = str(int(line[2:4], 16))
            items = line[4:]

            if items:
                items = [x.split(':') for x in items.split('|')]
                trueItems, args = ([], '')
                for (c, i) in items:
                    card = int(i, 16)
                    if card == 0:
                        args = c.replace('/', '+')
                    else:
                        trueItems.append([c, str(card)])
                itemsStr = '+'.join([':'.join(x) for x in trueItems])
            else:
                itemsStr = ''
                args = ''

            return '|'.join([indent, pred, player, itemsStr, args])

    def parseSupply(supply):
        items = supply.split('~')

        def parseItem(item):
            card = int(item[0:3], 16)
            count = int(item[3:])
            return '{}:{}'.format(count, card)
        return '~'.join([parseItem(item) for item in items])

    if postRen:
        log.version = 1
    else:
        log.version = 9
    log.log = '~'.join([parseLine(line) for line in lines])
    log.supply = parseSupply(log.supply)
    log.save()


class Command(BaseCommand):
    help = 'updates old logs'

    def handle(self, *args, **options):
        for log in GameLog.objects.filter(version=0):
            v0ToV1(log.game_id)
            self.stdout.write(self.style.SUCCESS(str(log.game_id)))
