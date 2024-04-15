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

if __name__ == '__main__':
    logs_path = "G:\\.shortcut-targets-by-id\\1CFpsGpqz65IlXdBeou1MB5lTdJbYxjv1\\Long Strange Trip runs\\Leftmost Attack Runs"
    # logs_path = "Leftmost Attack Runs"
    #pairs = []
    chains = []
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

        chain = []
        for game in games:
            lista = [m.attack_change for m in game.minions]
            opponent = lista[:7]
            player = lista[7:]
            pppp = [*opponent, *player]
            aaaa = []
            for i in range(len(pppp)):
                aaaa.append(pppp.index(i+1))
            chain.extend(aaaa)
        chains.append((chain, log_name))
        # minion_distributions(f"analysis/minion_{log_name}.txt", games)
        # rarity_distributions(f"analysis/rarity_{log_name}.txt", games)
        # minion_per_buff_distributions(f"analysis/minion_buff_{log_name}.txt", games)
        # legendaries_per_turn_distributions(f"analysis/leg_per_turn_{log_name}.txt", games)
        # minions_with_same_stats_distributions(f"analysis/same_stats_{log_name}.txt", games)
        # attack_values = []
        # for board in games:
        #    values = [m.attack_change for m in board.minions]
        #    for i in range(7):
        #        a, b = values[i], values[i + 7]
        #        values[i] = min(a,b)
        #        values[i + 7] = max(a,b)
        #    attack_values.append(values)
        # for key, value in groupby(attack_values, lambda values: str(values)):
        #    aa = list(value)
        #    if len(aa) > 1:
        #        print(key, aa)
        #first, *rest = games
        #prev_attack = game_to_attack(first)
        #for game in rest:
        #    current_attack = game_to_attack(game)
        #    pairs.append((prev_attack, current_attack))
        #    prev_attack = current_attack
    #grouped = defaultdict(list)
    #for before, after in pairs:
    #    grouped[f"{before[0]};{before[7]}"].append((before, after))
    #for key, value in grouped.items():
    #    if len(value) > 5:
    #        print(key)
    #        for a, b in value:
    #            print(a[:7], "->", b[:7])
    #            print(a[7:], "->", b[7:])
    #            pipe = [0] * 14
    #            for i, ball_before in enumerate(a):
    #                for j, ball_after in enumerate(b):
    #                    if ball_before == ball_after:
    #                        pipe[i] = j
    #            print(pipe)
    #            swap = a[7]
    #            a[7] = a[0]
    #            a[0] = swap
    #            pipe = [0] * 14
    #            for i, ball_before in enumerate(a):
    #                for j, ball_after in enumerate(b):
    #                    if ball_before == ball_after:
    #                        pipe[i] = j
    #            print(pipe)
    #            print("----------")
    with open('chains.txt', 'w') as f:
        for chain in chains:
            f.write(';'.join(map(str, chain[0])) + "\n")
    for first in range(len(chains)):
        for second in range(first + 1, len(chains)):
            chain1, name1 = chains[first]
            chain2, name2 = chains[second]
            longest = lcsubstring_length(chain1.copy(), chain2.copy())
            #print(chain1)
            #print(chain2)
            print(longest, (name1, name2))
    print("------------")
    #for i in range(len(common)):
    #    for j in range(i + 1, len(common)):
    #        longest = longest_common_subsequence(common[i].copy(), common[j].copy())
    #        print(len(longest), longest)
