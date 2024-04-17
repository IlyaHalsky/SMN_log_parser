import json
from collections import defaultdict
from dataclasses import dataclass

from tqdm import tqdm

from test import lehmer_code


# download from https://athena.hearthmod.com/apollo/mysterious

@dataclass
class LstGame:
    id: int
    username: str
    run_id: int
    tpe: int
    full_json: dict

    def __post_init__(self):
        self.broken = False
        if self.tpe == 1:
            self.game_type = '1to1'
        elif self.tpe == 2:
            self.game_type = 'reroll'
        else:
            raise Exception(f"Unknown game type: {self}")
        keys = list(map(int, self.full_json.keys()))
        if len(keys) != 14:
            self.broken = True
        self.start_id = min(keys)
        self.end_id = max(keys)
        self.attack_add = list(map(lambda v: v['AtkAdd'], self.full_json.values()))
        self.minion_names = list(map(lambda v: v['CardID'], self.full_json.values()))
        self.minions_set = frozenset(self.minion_names)
        if len(self.attack_add) < 14 or any([a == 0 for a in self.attack_add]):
            self.broken = True
        self.minions = list(self.full_json.values())
        keys = [self.username, self.run_id, self.tpe, self.game_type, self.start_id, self.end_id]
        self.for_hashing = ','.join(map(str, keys))

    @staticmethod
    def from_line(line: str):
        [id, user, game_id, tpe] = line.split("{", 1)[0].split(',')[:-1]
        json_raw = '{' + line.split("{", 1)[1]
        return LstGame(int(id), user, int(game_id), int(tpe), json.loads(json_raw))


def clean_data(boards):
    seen = set()
    seen2 = set()
    clean = []
    for board in boards:
        if not board.broken and board.for_hashing not in seen and json.dumps(board.full_json) not in seen2:
            seen.add(board.for_hashing)
            seen2.add(json.dumps(board.full_json))
            clean.append(board)
    return clean


def appearance_rates(boards):
    tpe = boards[0].game_type
    appeared = defaultdict(int)
    for board in boards:
        for minion in board.minions:
            appeared[minion['CardID']] += 1
    appeared = dict(sorted(appeared.items(), key=lambda item: item[1]))
    with open(f'csv_dump/appeared_times_{tpe}.txt', 'w') as w:
        for k, v in appeared.items():
            w.write(f"{k}, {v}\n")


def rarity_rates(boards):
    tpe = boards[0].game_type
    appeared = defaultdict(int)
    for board in boards:
        for minion in board.minions:
            appeared[minion['CardID']] += 1
    appeared = dict(sorted(appeared.items(), key=lambda item: item[1]))
    with open(f'csv_dump/appeared_times_{tpe}.txt', 'w') as w:
        for k, v in appeared.items():
            w.write(f"{k}, {v}\n")


def attack_add_counts(boards):
    tpe = boards[0].game_type
    counts = defaultdict(lambda: defaultdict(int))
    for board in boards:
        for minion in board.minions:
            counts[minion['CardID']][minion['AtkAdd']] += 1
    counts = dict(sorted(counts.items(), key=lambda item: item[0]))
    with open(f'csv_dump/attack_add_{tpe}.txt', 'w') as w:
        for k, v in counts.items():
            v = dict(sorted(v.items(), key=lambda item: item[0]))
            w.write(f'{k}, {v}\n')


def attack_add_counts_position(boards):
    tpe = boards[0].game_type
    counts = defaultdict(lambda: defaultdict(list))
    for board in boards:
        for i, minion in enumerate(board.minions):
            counts[minion['CardID']][minion['AtkAdd']].append(i)
    counts = dict(sorted(counts.items(), key=lambda item: item[0]))
    with open(f'csv_dump/attack_add_position_{tpe}.txt', 'w') as w:
        for k, v in counts.items():
            v = dict(sorted(v.items(), key=lambda item: item[0]))
            w.write(f'{k}, {v}\n')


def lehmer_code_calc(boards):
    final = []
    for board in boards:
        final.append((lehmer_code(board.attack_add), board.attack_add, board.minion_names))
    final.sort(key=lambda item: item[0])
    seen_codes = set()
    with open(f'csv_dump/lehmer.txt', 'w') as w:
        for l, a, m in final:
            if l in seen_codes:
                print("pooooog",l, a, m)
            else:
                seen_codes.add(l)
            w.write(f"{l};{a};{m}\n")


def rotate(l, n):
    return l[n:] + l[:n]


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
    boards = []
    with open('mysterious.csv', encoding="utf8") as csvfile:
        for line in tqdm(csvfile.readlines()):
            line = line[:-2]
            board = LstGame.from_line(line)
            boards.append(board)
    boards = clean_data(boards)
    print('total clean ', len(boards))
    one_to_one = [board for board in boards if board.game_type == '1to1']
    reset = [board for board in boards if board.game_type == 'reroll']
    print('1to1 ', len(one_to_one), 'reset ', len(reset))
    appearance_rates(one_to_one)
    appearance_rates(reset)
    attack_add_counts(one_to_one)
    attack_add_counts(reset)
    attack_add_counts_position(one_to_one)
    attack_add_counts_position(reset)
    lehmer_code_calc(boards)

    # attack repeats with made attack
    seen_attack = defaultdict(list)
    for board in one_to_one:
        attack_copy = board.attack_add.copy()
        #attack_copy[0], attack_copy[7] = attack_copy[7], attack_copy[0]
        attack_copy = [*attack_copy[:7], *list(reversed(attack_copy[7:]))]
        for i in range(14):
            attack_add = rotate(attack_copy, i)
            attack = ','.join(map(str, attack_add))
            seen_attack[attack].append(board)
        for i in range(14):
            attack_add = rotate(board.attack_add, i)
            attack = ','.join(map(str, attack_add))
            seen_attack[attack].append(board)
    printed = set()
    for key, value in seen_attack.items():
        if len(value) > 1:
            if ';'.join(map(str, map(lambda board: board.for_hashing, value))) in printed:
                continue
            else:
                printed.add(';'.join(map(str, map(lambda board: board.for_hashing, value))))
            print(key)
            for board in value:
                print(board)
                print(board.attack_add)
    ## attack repeats
    # seen_attack = defaultdict(list)
    # for board in boards:
    #   for i in range(7):
    #       attack_add = rotate(board.attack_add[:7], i)
    #       attack = ','.join(map(str, attack_add))
    #       seen_attack[attack].append(board)
    #   for i in range(7):
    #       attack_add = rotate(board.attack_add[7:], i)
    #       attack = ','.join(map(str, attack_add))
    #       seen_attack[attack].append(board)
    # pairs = defaultdict(list)
    # for key, value in seen_attack.items():
    #   if len(value) > 2:
    #       h_key = ';'.join([b.for_hashing for b in value])
    #       pairs[h_key].append((len(value), key, value))
    # for key, value in pairs.items():
    #    print(value)
    # for board in boards:
    #    if board.run_id == 1727089031:
    #        print(board)
    ## sizes
    # sizes = defaultdict(int)
    # for key, value in groupby(boards, key=lambda board: board.run_id):
    #    sizes[len(list(value))] += 1
    # sizes = dict(sorted(sizes.items(), key=lambda item: item[0]))
    # print(sizes)
    ## cyclic minions boards
    # seen_board = defaultdict(list)
    # for board in boards:
    #    for i in range(14):
    #        minions = rotate(board.minion_names, i)
    #        attack = ','.join(map(str, minions))
    #        seen_board[attack].append(board)
    # for key, value in seen_board.items():
    #    if len(value) > 1:
    #        print(key)
    #        for board in value:
    #            print(board)
    #            print(board.minion_names)
    ## the longest repeating minion sequence
    # repeating = defaultdict(lambda: defaultdict(int))
    # s = SequenceMatcher()
    # for i in tqdm(range(len(boards))):
    #   board1 = boards[i]
    #   for j in range(i + 1, len(boards)):
    #       board2 = boards[j]
    #       if board1.for_hashing != board2.for_hashing and not board1.minions_set.isdisjoint(board2.minions_set):
    #           s.set_seqs(board1.minion_names, board2.minion_names)
    #           a, b, size = s.find_longest_match()
    #           if size > 2:
    #               repeating[size][','.join(board1.minion_names[a: a + size])] += 1
    # repeating = dict(sorted(repeating.items(), key=lambda item: item[0], reverse=True))
    # for key, value in repeating.items():
    #   print(f'{key}: {value}')
    # the longest repeating number sequence
    # epeating = defaultdict(lambda: defaultdict(int))
    # s = SequenceMatcher()
    # for i in tqdm(range(len(one_to_one))):
    #   board1 = one_to_one[i]
    #   for j in range(i + 1, len(one_to_one)):
    #       board2 = one_to_one[j]
    #       if board1.for_hashing != board2.for_hashing:
    #           s.set_seqs(board1.attack_add, board2.attack_add)
    #           a, b, size = s.find_longest_match()
    #           if size > 4:
    #               repeating[size][','.join(map(str, board1.attack_add[a: a + size]))] += 1
    # epeating = dict(sorted(repeating.items(), key=lambda item: item[0], reverse=True))
    # or key, value in repeating.items():
    #   print(f'{key}: {value}')
    # attack_values = []
    # seen = set()
    # for board in one_to_one:
    #    values = board.attack_add.copy()
    #    for i in range(7):
    #        a, b = values[i], values[i + 7]
    #        values[i] = min(a, b)
    #        values[i + 7] = max(a, b)
    #    attack_values.append(values)
    #    if str(values) not in seen:
    #        seen.add(str(values))
    #    else:
    #        print(values)
    # for key, value in groupby(attack_values, lambda values: str(values)):
    #    aa = list(value)
    #    if len(aa) > 1:
    #        print(key, aa)
