from collections import defaultdict
from typing import List

from tqdm import tqdm

from lehmer_code import lehmer_code
from lehmer_db import lehmer_db_csv, lehmer_db_smn
from minions_utils import minions_by_id
from parse_lst import read_all_games, Runs, Run


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
        code = lehmer_code(game.attack_add)
        final.append((code, game.attack_add, game.minion_names))
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
    length = []
    for run in runs.all_sessions:
        length.append(len(run.games))
        curr = None
        for game in run.games:
            if curr is None:
                curr = game
            else:
                counts[compare_games(curr, game)] += 1
                curr = game
    counts = sort_value(counts)
    print(counts)
    print(length)


def count_tags(runs: Runs):
    tags_count = defaultdict(int)
    for game in runs.all_games:
        for minion in game.minions:
            for tag, _ in minion.tags:
                tags_count[tag] += 1
    tags_count = sort_value(tags_count)
    print(tags_count)


def decode_game(decode_dict, game):
    result = []
    for value in game.attack_add:
        result.append(decode_dict[value])
    return result


def lehmer_code_calc_decoded(runs):
    final = []
    for session in runs.all_sessions:
        first_game = session.games[0]
        decode_dict = {}
        for i, value in enumerate(first_game.attack_add):
            decode_dict[value] = i + 1
        for game in session.games:
            if game != first_game:
                decoded = decode_game(decode_dict, game)
                final.append((lehmer_code(decoded), decoded, game.minion_names))
                decoded2 = decoded.copy()
                decoded2[0], decoded2[7] = decoded2[7], decoded2[0]
                final.append((lehmer_code(decoded2), decoded2, game.minion_names))
    final.sort(key=lambda item: item[0])
    seen_codes = set()
    with open(f'analysis/lehmer_decoded.txt', 'w') as w:
        for l, a, m in final:
            if l in seen_codes:
                print("pooooog1", l, a, m)
            else:
                seen_codes.add(l)
            w.write(f"{l};{a};{m}\n")


def first_board_counts(runs):
    for session in runs.all_sessions:
        counts = defaultdict(int)
        first_minions = [m.card_id for m in session.games[0].minions]
        for game in session.games:
            for minion in game.minions:
                counts[minion.card_id] += 1
        counts = sort_value(counts, reversed=True)
        counts = list(counts.items())
        print(first_minions)
        place = []
        for minion in first_minions:
            place.append(next(i for i, v in enumerate(counts) if v[0] == minion))
        print(place)


def first_board_yours_print(runs: Runs):
    for session in runs.all_sessions[:5]:
        print(session.log_name)
        yours = session.games[0].attack_add[7:]
        count = 0
        for game in session.games:
            count += 1
            if count > 10:
                break
            print(count)
            attacks = game.attack_add
            result = ''
            for number in attacks[:7]:
                if number in yours:
                    result += f"{number} "
                else:
                    result += f"{number} "
            result += "\n"
            for number in attacks[7:]:
                if number in yours:
                    result += f"{number} "
                else:
                    result += f"{number} "
            print(result)


def first_board_yours(runs: Runs):
    repeats = defaultdict(int)
    target = [0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1]
    printer = []
    for session in runs.all_sessions:
        yours = session.games[0].attack_add[7:]
        before = None
        do_print = False
        for game in session.games:
            decoded = []
            for minion in game.attack_add:
                if minion in yours:
                    decoded.append(1)
                else:
                    decoded.append(0)
            if do_print:
                printer[-1].append(decoded)
                do_print = False
            if decoded == target:
                printer.append([session.log_name, before, decoded])
                do_print = True
            before = decoded
            repeats[','.join(map(str, decoded))] += 1

    for l, b, c, a in printer:
        print(l, "----------")
        print(f"{b[:7]}\n{b[7:]}\n")
        print(f"{c[:7]}\n{c[7:]}\n")
        print(f"{a[:7]}\n{a[7:]}")


def minions(runs: Runs):
    minions = set()
    for game in runs.all_games:
        for minion in game.minions:
            minions.add(minion.card_id)
    minions = list(minions)
    minions.sort()
    for m in minions:
        print(m, minions_by_id[m]['name'])


def lehmer_code_calc_with_swap(games):
    final = []
    for game in games:
        final.append((lehmer_code(game.attack_add), game.attack_add, game.minion_names))
        board = game.attack_add.copy()
        board[0], board[7] = board[7], board[0]
        final.append((lehmer_code(board), board, game.minion_names))
    final.sort(key=lambda item: item[0])
    seen_codes = set()
    with open(f'analysis/lehmer_swap.txt', 'w') as w:
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


def findLength(nums1: List[int], nums2: List[int]) -> int:
    N, M = len(nums1), len(nums2)

    def ok(k):
        # the idea is to use binary search to find the length `k`
        # then we check if there is any nums1[i : i + k] == nums2[i : i + k]
        s = set(tuple(nums1[i: i + k]) for i in range(N - k + 1))
        return any(tuple(nums2[i: i + k]) in s for i in range(M - k + 1))

    # init possible boundary
    l, r = 0, min(N, M)
    while l < r:
        # get the middle one
        # for even number of elements, take the upper one
        m = (l + r + 1) // 2
        if ok(m):
            # include m
            l = m
        else:
            # exclude m
            r = m - 1
    return l


def longestRepeatedSubstring(str):

    n = len(str)
    LCSRe = [[0 for x in range(n + 1)]
        for y in range(n + 1)]

    res = []  # To store result
    res_length = 0  # To store length of result

    # building table in bottom-up manner
    index = 0
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):

            # (j-i) > LCSRe[i-1][j-1] to remove
            # overlapping
            if (str[i - 1] == str[j - 1] and
                LCSRe[i - 1][j - 1] < (j - i)):
                LCSRe[i][j] = LCSRe[i - 1][j - 1] + 1

                # updating maximum length of the
                # substring and updating the finishing
                # index of the suffix
                if (LCSRe[i][j] > res_length):
                    res_length = LCSRe[i][j]
                    index = max(i, index)

            else:
                LCSRe[i][j] = 0

    # If we have non-empty result, then insert
    # all characters from first character to
    # last character of string
    if (res_length > 0):
        for i in range(
            index - res_length + 1,
            index + 1
        ):
            res.append(str[i - 1])

    return res


def prepare_game(game):
    result = game.attack_add
    result[0], result[7] = result[7], result[0]
    return result


def longest_common_chain(runs):
    chains = []
    for session in runs.all_sessions:
        chain = []
        for game in session.games:
            g = prepare_game(game)
            chain.extend(g)
        chains.append(chain)
    size = defaultdict(int)
    for i, chain1 in tqdm(enumerate(chains)):
        for j, chain2 in enumerate(chains):
            if j > i:
                size[findLength(chain1, chain2)] += 1
    size = sort_value(size)
    print(size)


def longest_common_chain_opponent(runs):
    chains = []
    for session in runs.all_sessions:
        chain = []
        for game in session.games:
            g = prepare_game(game)
            chain.extend(g[:7])
        chains.append(chain)
    size = defaultdict(int)
    for i, chain1 in tqdm(enumerate(chains)):
        for j, chain2 in enumerate(chains):
            if j > i:
                size[findLength(chain1, chain2)] += 1
    size = sort_value(size)
    print(size)


def longest_common_chain_player(runs):
    chains = []
    for session in runs.all_sessions:
        chain = []
        for game in session.games:
            g = prepare_game(game)
            chain.extend(g[7:])
        chains.append(chain)
    size = defaultdict(int)
    for i, chain1 in tqdm(enumerate(chains)):
        for j, chain2 in enumerate(chains):
            if j > i:
                size[findLength(chain1, chain2)] += 1
    size = sort_value(size)
    print(size)


def generate_boards(board):
    result = [board]
    for i in range(7):
        for j in range(7):
            new_board = board.copy()
            new_board[i], new_board[j + 7] = new_board[j + 7], new_board[i]
            result.append(new_board)
    return result


def lehmer_code_calc_one_move(games):
    final = []
    for game in games:
        for board in generate_boards(game.attack_add):
            final.append((lehmer_code(board), board, game.minion_names, game.attack_add))
    final.sort(key=lambda item: item[0])
    seen_codes = {}
    with open(f'analysis/lehmer_one_move.txt', 'w') as w:
        for l, a, m, o in final:
            if l in seen_codes:
                print("pooooog1", l, a, m, o, seen_codes[l])
            else:
                seen_codes[l] = (a, m, o)
            # if lehmer_db_csv.seen(l) is not None:
            #    print("pooooog2", l, a, m)
            # if lehmer_db_smn.seen(l) is not None:
            #    print("pooooog3", l, a, m)
            w.write(f"{l};{a};{m};{o}\n")


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


def loops_distribution(runs):
    loops = defaultdict(int)
    for game in runs.all_games:
        loops[find_loops(game.attack_add)] += 1
    loops = sort_key(loops)
    for k, v in loops.items():
        print(k, v / len(runs.all_games))


class Trip:
    def __init__(self):
        self.trip = []
        self.cards = []

    def init(self, minion, board):
        self.trip.append(minion.attack_change)
        self.cards.append(minion)
        self.last_board = board.attack_add

    def add_next(self, board):
        last = self.trip[-1]
        last_index = self.last_board.index(last)
        attack_add = board.attack_add
        minions = board.minions
        ## simple variant
        # self.trip.append(attack_add[last - 1])
        # self.minions.append(minions[last - 1].card_id)
        ## accounting for 1-1
        if last_index == 0:
            self.trip.append(attack_add[self.last_board[7] - 1])
            self.cards.append(minions[self.last_board[7] - 1])
        elif last_index == 7:
            self.trip.append(attack_add[self.last_board[0] - 1])
            self.cards.append(minions[self.last_board[0] - 1])
        else:
            self.trip.append(attack_add[last - 1])
            self.cards.append(minions[last - 1])
        self.last_board = attack_add

    @property
    def minions(self):
        return [m.card_id for m in self.cards]

    @property
    def rarity(self):
        return [m.rarity for m in self.cards]

    @property
    def expansion(self):
        return [m.expansion for m in self.cards]

    @staticmethod
    def init_trips(board):
        trips = []
        for minion in board.minions:
            trip = Trip()
            trip.init(minion, board)
            trips.append(trip)
        return trips


def build_trips(session: Run):
    trips = []
    first = True
    for game in session.games:
        if first:
            trips = Trip.init_trips(game)
            first = False
        else:
            for trip in trips:
                trip.add_next(game)
    return trips


def common_trips(runs: Runs):
    all_trips = []
    for session in runs.all_sessions:
        all_trips.extend(build_trips(session))
    size = defaultdict(int)
    for i, trip1 in enumerate(tqdm(all_trips)):
        for j, trip2 in enumerate(all_trips):
            if j > i:
                length = findLength(trip1.trip, trip2.trip)
                # if length >= 8:
                #    print(length)
                #    print(trip1)
                #    print(trip2)
                size[length] += 1
    size = sort_key(size)
    print(size)

def common_trips_minions(runs: Runs):
    all_trips = []
    for session in runs.all_sessions:
        all_trips.extend(build_trips(session))
    size = defaultdict(int)
    for i, trip1 in enumerate(tqdm(all_trips)):
        for j, trip2 in enumerate(all_trips):
            if j > i:
                length = findLength(trip1.expansion, trip2.expansion)
                # if length >= 8:
                #    print(length)
                #    print(trip1)
                #    print(trip2)
                size[length] += 1
    size = sort_key(size)
    print(size)


def repeating_sub_trips(runs: Runs):
    all_trips = []
    for session in runs.all_sessions:
        all_trips.extend(build_trips(session))
    for trip in tqdm(all_trips):
        repeat = longestRepeatedSubstring(trip.trip)
        if len(repeat) > 5:
            print(repeat, len(trip.trip))


def paired_occurrence(runs: Runs):
    minion_pairs = defaultdict(lambda: defaultdict(int))
    for session in runs.all_sessions:
        last = None
        for game in session.games:
            if last is None:
                last = game
            else:
                for i, minion in enumerate(last.minions):
                    for j, minion2 in enumerate(game.minions):
                        if True:
                            id1 = minion.card_id
                            id2 = minion2.card_id
                            f = min(id1, id2)
                            s = max(id1, id2)
                            minion_pairs[f][s] += 1
                last = game
    result = defaultdict(int)
    counts = defaultdict(int)
    for k, v in minion_pairs.items():
        k_name = minions_by_id[k]['name']
        v = sort_value(v)
        for k2, v2 in v.items():
            k2_name = minions_by_id[k2]['name']
            result[f"{k};{k2};{k_name};{k2_name};{v2}\n"] = v2
            counts[v2] += 1
    with open(f'analysis/minions_on_same_board.txt', 'w') as w:
        result = sort_value(result, reversed=True)
        for k, v in result.items():
            w.write(f"{k}")
    counts = sort_key(counts)
    print(counts)

def set_distribution(runs):
    set_count = defaultdict(int)
    set_size = defaultdict(lambda: set())
    for game in runs.all_games:
        for m in game.minions:
            exp = m.card_id.split("_")[0]
            set_count[exp] += 1
            set_size[exp].add(m.card_id)
    set_size = sort_key(set_size)
    set_count = sort_key(set_count)
    for k, v in set_size.items():
        print(k, len(v), set_count[k])

if __name__ == '__main__':
    runs = read_all_games(
        "G:\\.shortcut-targets-by-id\\1CFpsGpqz65IlXdBeou1MB5lTdJbYxjv1\\Long Strange Trip runs\\Leftmost Attack Runs",
        [],
    )
    lehmer_code_calc(runs.all_games)
    print(f"Total turns: {len(runs.all_games)}")
    # together_counts(runs)
    # sticky_distributions(runs)
    # lehmer_code_calc_decoded(runs)
    # first_board_counts(runs)
    # first_board_yours(runs)
    # minions(runs)
    # lehmer_code_calc_with_swap(runs.all_games)
    # lehmer_code_calc_decoded(runs)
    # longest_common_chain(runs)
    # longest_common_chain_opponent(runs)
    # longest_common_chain_player(runs)
    # lehmer_code_calc_one_move(runs.all_games)
    # loops_distribution(runs)
    # common_trips(runs)
    #repeating_sub_trips(runs)
    #common_trips_minions(runs)
    # for session in runs.all_sessions:
    #    trips = build_trips(session)
    #    for trip in trips:
    #        print(trip.trip)
    #    for board in session.games:
    #        print(board.attack_add)
    #    break
    #paired_occurrence(runs)
    set_distribution(runs)