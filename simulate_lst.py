import random
from collections import defaultdict


def get_board():
    return list(random.choices(range(3000), k=14))


def compare_board(one, two):
    score = 0
    for i in range(14):
        if one[i] == two[i]:
            score += 1
    return score

def sort_key(input):
    return dict(sorted(input.items(), key=lambda item: item[0]))

if __name__ == '__main__':
    boards = []
    for i in range(50):
        filtered = list(filter(lambda x: x<14,get_board()))
        if len(filtered)>0:
            print("meh")

    #distribution = defaultdict(int)
    #for i, board1 in enumerate(boards):
    #    if i == len(boards) - 1:
    #        break
    #    best_score = -1
    #    best = None
    #    best_index = None
    #    for j, board2 in enumerate(boards):
    #        if i >= j:
    #            continue
    #        if compare_board(board1, board2) > best_score:
    #            best_score = compare_board(board1, board2)
    #            best = board2
    #            best_index = j
    #    distribution[best_score] += 1
    #    print(best_score, i, best_index, best_index - i, board1, best)
#
    #print(sort_key(distribution))