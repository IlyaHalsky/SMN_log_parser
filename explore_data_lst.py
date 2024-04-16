import os
from collections import defaultdict
from difflib import SequenceMatcher
from itertools import groupby
from operator import attrgetter as atr

from tqdm import tqdm

from smn_game import Game
from smn_logs import read_log_file


def sort_key(input):
    return dict(sorted(input.items(), key=lambda item: item[0]))


def sort_value(input):
    return dict(sorted(input.items(), key=lambda item: item[1]))


def minion_distributions(file_name, games):
    counts = defaultdict(int)
    for g in games:
        for minion in g.minions:
            counts[minion.card_id] += 1
    counts = sort_value(counts)
    with open(file_name, 'w') as f:
        for key, value in counts.items():
            f.write('{},{}\n'.format(key, value))


def rarity_distributions(file_name, games):
    counts = defaultdict(int)
    for g in games:
        for minion in g.minions:
            counts[minion.rarity] += 1
    counts = sort_value(counts)
    with open(file_name, 'w') as f:
        for key, value in counts.items():
            f.write('{},{}\n'.format(key, value))


def minion_per_buff_distributions(file_name, games):
    counts = defaultdict(lambda: defaultdict(int))
    for g in games:
        for minion in g.minions:
            counts[minion.card_id][minion.attack_change] += 1
    counts = sort_key(counts)
    with open(file_name, 'w') as f:
        for key, value in counts.items():
            f.write('{},{}\n'.format(key, value))


def legendaries_per_turn_distributions(file_name, games):
    per_turn = defaultdict(int)
    for g in games:
        total = 0
        for minion in g.minions:
            if minion.rarity == 'LEGENDARY':
                total += 1
        per_turn[total] += 1
    per_turn = sort_key(per_turn)
    with open(file_name, 'w') as f:
        for key, value in per_turn.items():
            f.write('{},{}\n'.format(key, value))


def minions_with_same_stats_distributions(file_name, games):
    per_turn = defaultdict(int)
    for g in games:
        total = 0
        same_base_stats = set()
        for minion in g.minions:
            base_stats = ','.join(map(str, [minion.attack, minion.health, minion.mana]))
            if base_stats in same_base_stats:
                total += 1
            else:
                same_base_stats.add(base_stats)
        per_turn[total] += 1
    per_turn = sort_key(per_turn)
    with open(file_name, 'w') as f:
        for key, value in per_turn.items():
            f.write('{},{}\n'.format(key, value))


def game_to_attack(game):
    return [m.attack_change for m in game.minions]


def lcsubstring_length(a, b):
    table = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    longest = 0
    for i, ca in enumerate(a, 1):
        for j, cb in enumerate(b, 1):
            if ca == cb:
                length = table[i][j] = table[i - 1][j - 1] + 1
                longest = max(longest, length)
    return longest

def rotate(l, n):
    return l[n:] + l[:n]

def game_to_board(game):
    if game is None:
        return None
    return [m.attack_change for m in game.minions]

def compare_games(g1, g2):
    one = game_to_board(g1)
    two = game_to_board(g2)
    score = 0
    for i in range(len(one)):
        if one[i] == two[i]:
            score += 1
    return score

if __name__ == '__main__':
    logs_path = "G:\\.shortcut-targets-by-id\\1CFpsGpqz65IlXdBeou1MB5lTdJbYxjv1\\Long Strange Trip runs\\Leftmost Attack Runs"
    # logs_path = "Leftmost Attack Runs"

    for log_file in tqdm(os.listdir(logs_path)):
        log_path = os.path.join(logs_path, log_file)
        if os.path.isdir(log_path):
            continue
        minions = read_log_file(log_path)
        log_name = log_file.rsplit('.', 1)[0]

        games = []
        carry_over = []
        for list_id, minions_group in groupby(minions.values(), lambda minion: minion.list_id):
            minions_list_all = [minion for minion in list(minions_group)]
            minions_list = [minion for minion in minions_list_all if not minion.child_card]
            only_minions_list = [minion for minion in minions_list if not minion.spell]
            if len(only_minions_list) != 14:
                if len(only_minions_list) > 0 and only_minions_list[-1].card_id == 'SCH_199':
                    carry_over = only_minions_list
                    continue
                if len(carry_over) == 0:
                    continue
                else:
                    only_minions_list = [*only_minions_list, *carry_over]
                    carry_over = []
                    if len(only_minions_list) != 14:
                        continue

            only_minions_list.sort(key=atr('sort_key'))
            game = Game(only_minions_list, [])
            if not game.lst_complete:
                continue
            games.append(game)

        distribution = defaultdict(int)
        for i, game1 in enumerate(games):
            if i + 1 == len(games):
                break
            best_score = -1
            best = None
            best_index = None
            for j, game2 in enumerate(games):
                if i >= j:
                    continue
                if compare_games(game1, game2) > best_score:
                    best_score = compare_games(game1, game2)
                    best = game2
                    best_index = j
            print(best_score, i, best_index, best_index - i, game_to_board(game1), game_to_board(best))
            distribution[best_score] += 1
        print(sort_key(distribution))
        break




