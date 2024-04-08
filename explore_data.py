import os
import re
from collections import deque, defaultdict
from itertools import groupby

import cv2
from hearthstone.enums import CardSet
from tqdm import tqdm

from card_sets import set_names
from smn_game import Game
from smn_logs import read_log_file, minions_json, minions_by_id
from visualize import create_board_image

def sanitize_filename(filename):
    return re.sub('[^0-9a-zA-Z. ]+', '_', filename)

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
    for log_file in tqdm(os.listdir(logs_path)):
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

            special = False
            #find = 'Miracle Salesman'
            #for minion in game.minions:
            #    if minion.name == find:
            #        special = True
            #        minion.color[0] = 255
            #for spell in game.spells:
            #    if spell.name == find:
            #        special = True
            #        spell.color[0] = 255

            has_dups = False
            duplicate_id = None

            #group_by = lambda card: card.name
            group_by = lambda card: card.card_id
            grouped = defaultdict(list)
            for spell in game.spells:
                grouped[group_by(spell)].append(spell)
            for key, value in grouped.items():
                if len(value) > 1:
                    duplicates.append(key)
                    for card in value:
                        card.color[1] = 255
                    for minion in game.minions:
                        if group_by(minion) == key:
                            minion.color[1] = 255
                    has_dups = True
                    duplicate_id = key

            grouped2 = defaultdict(list)
            for minion in game.minions:
                grouped2[group_by(minion)].append(minion)
            for key, value in grouped2.items():
                if len(value) > 1:
                    duplicates.append(key)
                    for card in value:
                        card.color[1] = 255
                    for minion in game.minions:
                        if group_by(minion) == key:
                            minion.color[1] = 255
                    has_dups = True
                    duplicate_id = key



            game_number += 1
            if has_dups or special:
                sanitized = sanitize_filename(log_file)
                images_path = f"{logs_path}/duplicate_images"
                if not os.path.exists(images_path):
                    os.makedirs(images_path)
                if special:
                    board = create_board_image(game)
                    board = cv2.resize(board, (0, 0), fx=0.5, fy=0.5)
                    cv2.imwrite(
                        images_path + "/" + 'ms-' + sanitized.replace(".log", "") + '-' + str(list_id) + ".jpg", board
                    )
                elif has_dups:
                    print(log_name, list_id, duplicate_id)
                    file = f"{images_path}/{duplicate_id}-{minions_by_id[duplicate_id]['name']}-{sanitized.replace('.log', '')}-{list_id}.jpg"
                    if not os.path.exists(file):
                        board = create_board_image(game)
                        #board = cv2.resize(board, (0, 0), fx=0.5, fy=0.5)
                        cv2.imwrite(file, board)
    print(game_count)
    with open("dups_done.txt", mode='wt', encoding='utf-8') as f:
        f.write('\n'.join(read_logs))
    for duplicate_id in duplicates:
        print(duplicate_id, minions_by_id[duplicate_id]['name'])
    # with open('edges.csv', 'w') as f:
    #    f.write('Source,Target,Type,Id,Label,Weight' + '\n')
    #    line_no = 0
    #    for k, v in edges.items():
    #        f.write(f'{k[0]},{k[1]},Undirected,{line_no},,{v}.0\n')
    #        line_no += 1
    # with open('nodes.csv', 'w') as f:
    #    f.write('Id,Label,Interval' + '\n')
    #    for k, v in minions_by_dbfId:
    #        f.write(f'{k},{v['name']},\n')
    #        line_no += 1
