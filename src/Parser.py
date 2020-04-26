# -*- coding: utf-8 -*-
from .Enums import *
from .Utils import *
from .Preds import *


def itemsToDict(items):
    if items == "":
        return {}
    else:
        return {int(i.split(":")[1]): int(i.split(":")[0]) for i in items.split("+")}


def merge_lines(lines):
    minimal_count = -1
    best_backs = 0
    best_line = None

    for line in lines:
        items = itemsToDict(line.split("|")[-2])
        count = sum(items.values())
        if (
            minimal_count < 0
            or count < minimal_count
            or (count == minimal_count and items.get(0, 0) < best_backs)
        ):
            best_line = line
            best_backs = items.get(0, 0)
            minimal_count = count
    return best_line


def combined_parse(logString):
    logs = [l.split("~") for l in logString.split("###")]

    actualLength = min([len(log) for log in logs])
    mergedLines = [merge_lines([log[i] for log in logs]) for i in range(actualLength)]

    return "~".join(mergedLines)


def parse_header(headerString):
    data = headerString.split(":", 1)
    return (data[0], data[1])


class Printer:
    def __init__(self, version):
        self.cards, self.preds = getInfo(version)

    def print_supply(self, supply):
        def parse(item):
            parts = item.split(":")
            return "{} {}".format(parts[0], self.cards[int(parts[1])])

        items = supply.split("~")
        parsedItems = [parse(item) for item in items if item]
        return "Supply: " + ", ".join(parsedItems)

    def print_items(self, inString):
        def parse(item):
            parts = item.split(":")
            if len(parts) == 1:
                return parts[0]
            else:
                return "{} {}".format(parts[0], self.cards[int(parts[1])])

        items = inString.split("+")

        parsedItems = [parse(item) for item in items]
        return ", ".join(parsedItems)

    def print_args(self, inString, predName):
        def parse(item, argType):
            parts = item.split(":")
            if len(parts) == 1:
                if argType == argTypes.NUMBER:
                    return parts[0]
                else:
                    return self.cards[int(parts[0])]
            else:
                return "{} {}".format(parts[0], self.cards[int(parts[1])])

        items = inString.split("+")
        args = getArgTypes(predName)

        if args:
            parsedItems = [parse(item, args[i]) for (i, item) in enumerate(items)]
        else:
            parsedItems = [item.replace(":", " ") for item in items]
        return ", ".join(parsedItems)

    def print_line(self, line):
        indent, pred, player, items, args = line.split("|")
        if args:
            return "P{} - {} ({}): {}".format(
                player,
                self.preds[int(pred)],
                self.print_args(args, self.preds[int(pred)]),
                self.print_items(items),
            )
        else:
            if items:
                return "P{} - {}: {}".format(
                    player, self.preds[int(pred)], self.print_items(items)
                )
            else:
                return "P{} - {}".format(player, self.preds[int(pred)])
