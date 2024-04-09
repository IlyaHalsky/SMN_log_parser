import os
import re
from collections import defaultdict
from itertools import groupby

from tqdm import tqdm

from smn_game import Game
from smn_logs import read_log_file
from operator import attrgetter as atr


def sanitize_filename(filename):
    return re.sub('[^0-9a-zA-Z. ]+', '_', filename)


if __name__ == '__main__':

    # if os.path.exists("dups_done.txt"):
    #    with open("dups_done.txt", "r") as f:
    #        read_logs = f.read().splitlines()
    # else:
    #    read_logs = []

    logs_path = "G:/.shortcut-targets-by-id/1CFpsGpqz65IlXdBeou1MB5lTdJbYxjv1/Long Strange Trip runs"
    game_count = 0
    duplicates = []
    patterns = defaultdict(int)
    # edges = defaultdict(int)
    for log_file in tqdm(os.listdir(logs_path)):
        # if sanitize_filename(log_file) in read_logs:
        #    continue
        # else:
        #    read_logs.append(sanitize_filename(log_file))
        # minion_repeats = defaultdict(list)
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
            if len(minions_list) < 14:
                continue

            only_minions_list.sort(key=atr('sort_key'))
            game = Game(only_minions_list, only_spells_list)
            if not game.lst_complete:
                continue
            game_count += 1
            values = list(map(lambda m: m.attack_change, game.opponents_board))
            values.sort()
            values = list(map(lambda x: f'{x:02}', values))
            patterns[','.join(values)] += 1
    print(game_count)
    patterns = dict(sorted(patterns.items()))
    for k, v in patterns.items():
        print(k, v)
    # with open("dups_done.txt", mode='wt', encoding='utf-8') as f:
    #    f.write('\n'.join(read_logs))
    # for duplicate_id in duplicates:
    #    print(duplicate_id, minions_by_id[duplicate_id]['name'])
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
