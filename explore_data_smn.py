import os
import re
from collections import deque, defaultdict
from itertools import groupby

import cv2
from hearthstone.enums import CardSet
from tqdm import tqdm

from card_sets import set_names
from lehmer_db import lehmer_db_csv
from smn_game import Game
from smn_logs import read_log_file
from minions_utils import minions_json, minions_by_id
from test import lehmer_code
from visualize import create_board_image

def sanitize_filename(filename):
    return re.sub('[^0-9a-zA-Z. ]+', '_', filename)

def lehmer_code_calc(games):
    final = []
    for game in games:
        try:
            correct = [m.card_id for m in game.correct_smn_answers]
            attack_add = []
            for minion in game.minions:
                attack_add.append(correct.index(minion.card_id) + 1)
            final.append((lehmer_code(attack_add), attack_add, game.minion_names))
        except:
            continue
    final.sort(key=lambda item: item[0])
    seen_codes = set()
    with open(f'analysis/lehmer_smn.txt', 'w') as w:
        for l, a, m in final:
            if l in seen_codes:
                print("pooooog", l, a, m)
            else:
                seen_codes.add(l)
            if lehmer_db_csv.seen(l) is not None:
                print("pooooog", l, a, m)
            w.write(f"{l};{a};{m}\n")

if __name__ == '__main__':

    if os.path.exists("dups_done.txt"):
        with open("dups_done.txt", "r") as f:
            read_logs = f.read().splitlines()
    else:
        read_logs = []

    logs_path = "G:/.shortcut-targets-by-id/1AW0W0amolgf4yzIMhgs_fcpbkvR37Tqz/Say My Name runs"
    game_count = 0
    duplicates = []
    #edges = defaultdict(int)
    all_games = []
    for log_file in tqdm(os.listdir(logs_path)):
        try:
            if sanitize_filename(log_file) in read_logs:
                continue
            else:
                read_logs.append(sanitize_filename(log_file))
            minion_repeats = defaultdict(list)
            game_number = 0
            log_path = os.path.join(logs_path, log_file)
            if os.path.isdir(log_path):
                continue
            minions = read_log_file(log_path)
            log_name = log_file.rsplit('.', 1)[0]
            current_list = -1
            for list_id, minions_group in groupby(minions.values(), lambda minion: minion.list_id):
                minions_list_all = [minion for minion in list(minions_group)]
                minions_list = [minion for minion in minions_list_all if not minion.child_card]
                only_minions_list = [minion for minion in minions_list if not minion.spell]
                only_spells_list = [minion for minion in minions_list if minion.spell]
                if len(minions_list) < 34:
                    continue
                if any([spell.name == '???' for spell in only_spells_list]):
                    continue
                game_count += 1
                minions_list.sort(key=lambda minion: minion.id)
                game = Game(only_minions_list, only_spells_list)
                all_games.append(game)
        except:
            continue
    #lehmer_code_calc(all_games)
    for game in all_games:
        print(game.game_id)
        for minion in game.minions:
            print(minion)
        for spell in game.spells:
            print(spell)



