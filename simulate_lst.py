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

def find_loops(attack_add):
    used = set()
    loops = []
    for i, attack in enumerate(attack_add):
        if attack not in used:
            loop = [attack]
            used.add(attack)
            next_ind = attack - 1
            while attack_add[next_ind] not in used:
                current_value = attack_add[next_ind]
                loop.append(current_value)
                used.add(current_value)
                next_ind = current_value - 1
            loops.append(loop)
    return len(loops)

if __name__ == '__main__':
    sims = 100000
    number_of_loops = defaultdict(int)
    boards = []
    for i in range(sims):
        boards.append(get_board())
    for board in boards:
        number_of_loops[find_loops(board)] += 1
    number_of_loops = sort_key(number_of_loops)
    for k, v in number_of_loops.items():
        print(k, v / sims)
