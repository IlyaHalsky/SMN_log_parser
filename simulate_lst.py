import random
from collections import defaultdict


def get_board():
    return list(random.sample(range(14), k=14))


def compare_board(one, two):
    result = [0] * 14
    for i in range(14):
        if one[i] == two[i]:
            result[i] = 1
    return result

def get_count(one, two):
    count = 0
    for i in range(14):
        if one[i] == two[i]:
            count += 1
    return count


def sort_key(input):
    return dict(sorted(input.items(), key=lambda item: item[0]))


def sort_value(input):
    return dict(sorted(input.items(), key=lambda item: item[1]))


if __name__ == '__main__':
    maximums = defaultdict(int)
    one_is_more = 0
    average = defaultdict(int)
    sims = 1000
    for i in range(sims):
        turns = [199, 249, 198, 130, 200, 198, 553, 201, 299, 809, 399, 772, 277, 468, 410, 315, 502, 329, 811, 28, 793, 488, 298, 298, 297, 298, 201, 201, 251, 251, 246, 248, 199, 201, 198, 201, 304, 149, 150, 150, 149, 200, 200, 200, 201, 201, 197]
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
                    repeats[get_count(last, board)] += 1
                    last = board
        repeats = sort_value(repeats)
        for k, v in repeats.items():
            average[k] += v
        if repeats[1] > repeats[0]:
            one_is_more += 1
        print(repeats)
    print(one_is_more, 1000)
    for k in average.keys():
        average[k] = int(average[k] / sims)
    average = sort_value(average)
    print(average)