from collections import defaultdict

from lehmer_code import lehmer_code
from lehmer_db import lehmer_db_csv, lehmer_db_smn
from parse_lst import read_all_games, Runs


def sort_key(input):
    return dict(sorted(input.items(), key=lambda item: item[0]))


def sort_value(input, reversed=False):
    return dict(sorted(input.items(), key=lambda item: item[1], reverse=reversed))


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


def lehmer_code_calc(games):
    final = []
    for game in games:
        final.append((lehmer_code(game.attack_add), game.attack_add, game.minion_names))
    final.sort(key=lambda item: item[0])
    seen_codes = set()
    with open(f'analysis/lehmer.txt', 'w') as w:
        for l, a, m in final:
            if l in seen_codes:
                print("pooooog1", l, a, m)
            else:
                seen_codes.add(l)
            if lehmer_db_csv.seen(l) is not None:
                print("pooooog2", l, a, m)
            if lehmer_db_smn.seen(l) is not None:
                print("pooooog3", l, a, m)
            w.write(f"{l};{a};{m}\n")


def compare_boards(g1, g2):
    a1 = g1.attack_add
    a2 = g2.attack_add
    similar = [0] * 14
    for i in range(14):
        similar[i] = 1 if a1[i] == a2[i] else 0
    return similar


def solution(opponent, player):
    o_s = sum(opponent)
    p_s = sum(player)
    best_diff = abs(o_s - p_s)
    best_move = [-1, -1, -1, -1, -1, -1]
    for i, o in enumerate(opponent):
        for j, p in enumerate(player):
            o_n = o_s - o + p
            p_n = p_s - p + o
            diff = abs(o_n - p_n)
            if diff <= best_diff:
                best_move = [p, o, j + 1, i + 1, p_n, o_n]
                best_diff = diff
    return best_move, best_diff


def together_counts(runs: Runs):
    together = defaultdict(lambda: defaultdict(int))
    for game in runs.all_games:
        minion_ids = [m.card_id for m in game.minions]
        for minion in minion_ids:
            for other in minion_ids:
                if minion != other:
                    together[minion][other] += 1
    together = sort_key(together)
    with open('analysis/together.txt', 'w') as w:
        for key, value in together.items():
            value = sort_value(value, reversed=True)
            w.write('{},{}\n'.format(key, value))


def sticky_distributions(runs: Runs):
    counts = defaultdict(int)
    for run in runs.all_sessions:
        curr = None
        for game in run.games:
            if curr is None:
                curr = game
            else:
                counts[compare_games(curr, game)] += 1
                curr = game
    counts = sort_value(counts)
    print(counts)


def count_tags(runs: Runs):
    tags_count = defaultdict(int)
    for game in runs.all_games:
        for minion in game.minions:
            for tag, _ in minion.tags:
                tags_count[tag] += 1
    tags_count = sort_value(tags_count)
    print(tags_count)


if __name__ == '__main__':
    runs = read_all_games(
        "G:\\.shortcut-targets-by-id\\1CFpsGpqz65IlXdBeou1MB5lTdJbYxjv1\\Long Strange Trip runs\\Leftmost Attack Runs",
        [],
    )
    lehmer_code_calc(runs.all_games)
    print(f"Total turns: {len(runs.all_games)}")
    #together_counts(runs)
    sticky_distributions(runs)
