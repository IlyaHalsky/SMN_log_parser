import random
from collections import defaultdict


def get_board():
    return list(random.choices(range(14), k=14))


def compare_board(one, two):
    result = [0] * 14
    for i in range(14):
        if one[i] == two[i]:
            result[i] = 1
    return result


def sort_key(input):
    return dict(sorted(input.items(), key=lambda item: item[0]))


def sort_value(input):
    return dict(sorted(input.items(), key=lambda item: item[1]))


if __name__ == '__main__':
    maximums = defaultdict(int)
    all_counts = defaultdict(int)
    one_is_more = 0
    average = defaultdict(int)
    for i in range(1000):
        turns = [199,249,198,130,200,198,553,201,299,809,399,772,277,468,410,315,502,329,811,28,793,488,298,298,297,298,201,201, *[729, 324, 457, 833, 221, 271, 220, 1320, 828, 161, 198]]
        repeats = defaultdict(int)
        for turn in turns:
            boards = []
            for i in range(turn):
                boards.append(get_board())
            last = None
            for board in boards:
                if last is None:
                    last = board
                else:
                    repeats[','.join(map(str, compare_board(last, board)))] += 1
                    last = board
        repeats = sort_value(repeats)
        totals = defaultdict(int)
        for k, v in repeats.items():
            totals[k.count('1')] += v
        totals = sort_value(totals)
        for k, v in totals.items():
            maximums[k] = max(v, maximums[k])
            all_counts[k] +=1
            average[k] += v
        if totals[1] > totals[0]:
            one_is_more += 1
        print(totals)
    print(maximums)
    print(all_counts)
    print({8: 1, 7: 1, 6: 10, 5: 60, 4: 238, 3: 1010, 2: 2936, 1: 5696, 0: 5792})
    print(one_is_more, 1000)
    for k in average.keys():
        average[k] = int(average[k] / 1000)
    average = sort_value(average)
    print(average)