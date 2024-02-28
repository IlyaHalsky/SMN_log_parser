import os
import platform
from itertools import groupby

from smn_logs import WIN_LOG_PATH, MAC_LOG_PATH, read_log_file

if __name__ == '__main__':
    base_path = WIN_LOG_PATH if platform.system() == 'Windows' else MAC_LOG_PATH
    board_set = set()
    correct_set = set()
    incorrect_set = set()
    for log_folder in os.listdir(base_path):
        log_path = os.path.join(base_path, log_folder, 'Zone.log')
    #logs_path = "logs"
    #for log_file in os.listdir(logs_path):
    #    log_path = os.path.join(logs_path, log_file)
    #    if os.path.isdir(log_path):
    #        continue
        minions = read_log_file(log_path)

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
    with open('incorrect_set.txt', 'w') as file:
        to_print = sorted(incorrect_set)
        for minion in to_print:
            file.write(minion + "\n")
