import os
import platform
import re
from dataclasses import dataclass
from itertools import groupby

from smn_logs import WIN_LOG_PATH, MAC_LOG_PATH, extract_message, parse_minion

if __name__ == '__main__':
    base_path = WIN_LOG_PATH if platform.system() == 'Windows' else MAC_LOG_PATH
    board_set = set()
    correct_set = set()
    incorrect_set = set()
    for log_folder in os.listdir(base_path):
        list_num = 0
        list_offset = 0
        log_path = os.path.join(base_path, log_folder, 'Zone.log')
        minions = {}
        with open(log_path) as file:
            for line_n in file:
                line = line_n[:-1]
                type, message = extract_message(line)
                if type == 'list-start':
                    if message >= list_num:
                        list_num = message
                    else:
                        list_offset = list_offset + 100000
                        list_num = message
                if type == 'list-item':
                    parse_minion(message, minions, list_offset)
        current_list = -1

        for list_id, minions_group in groupby(minions.values(), lambda minion: minion.list_id):
            minions_list_all = [minion for minion in list(minions_group)]
            minions_list = [minion for minion in minions_list_all if not minion.child_card]
            only_minions_list = [minion for minion in minions_list if not minion.spell]
            only_spells_list = [minion for minion in minions_list if minion.spell]
            if len(minions_list) < 34:
                continue
            minions_list.sort(key=lambda minion: minion.id)
            if list_id != current_list:
                print(f"T:{list_id} {len(minions_list)}")

            for minion in only_minions_list:
                board_set.add(minion.name)
            for spell in only_spells_list:
                if any(spell.name == minion.name for minion in only_minions_list):
                    correct_set.add(spell.name)
                else:
                    incorrect_set.add(spell.name)

    with open('board_set.txt', 'w') as file:
        to_print = sorted(board_set)
        for minion in to_print:
            file.write(minion + "\n")
    with open('correct_set.txt', 'w') as file:
        to_print = sorted(correct_set)
        for minion in to_print:
            file.write(minion + "\n")
    with open('incorrect_set.txt', 'w') as file:
        to_print = sorted(incorrect_set)
        for minion in to_print:
            file.write(minion + "\n")


