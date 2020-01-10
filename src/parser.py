
def parse_items(items):
    if items == '':
        return {}
    else:
        return {i.split(':')[1]: i.split(':')[0] for
                i in items.split('+')}


def merge_lines(lines):
    minimal_count = -1
    best_backs = 0
    best_line = None

    for line in lines:
        items = parse_items(line.split('|')[-2])
        count = sum(items.values())
        if minimal_count < 0 or count < minimal_count or \
                (count == minimal_count and items.get(0, 0) < best_backs):
            best_line = line
            best_backs = items.get(0, 0)
            minimal_count = count
    return best_line


def combined_parse(logString):
    logs = [l.split('~') for l in logString.split('###')]

    actualLength = min([len(log) for log in logs])
    mergedLines = [merge_lines([log[i] for log in logs])
                   for i in range(actualLength)]

    return '\n'.join(mergedLines)


def parse_header(headerString):
    data = headerString.split(":", 1)
    return (data[0], data[1].split("~"))
