import platform
import time
from itertools import groupby
from operator import attrgetter as atr
from typing import Iterator, List

import psutil
from tabulate import tabulate

from smn_logs import extract_message, parse_minion, Minion


def hs_running():
    for pid in psutil.pids():
        if psutil.pid_exists(pid):
            if 'Hearthstone.exe' in psutil.Process(pid).name():
                return True
    return False


def follow(file, sleep_sec=0.1) -> Iterator[str]:
    """ Yield each line from a file as they are written.
    `sleep_sec` is the time to sleep after empty reads. """
    line = ''
    while True:
        tmp = file.readline()
        if tmp is not None and tmp != "":
            line += tmp
            if line.endswith("\n"):
                yield line
                line = ''
        elif hs_running():
            time.sleep(sleep_sec)
        else:
            break
    yield ''


def print_game(minions: List[Minion]):
    header = '-' * 40
    opponent_board = minions[:7]
    opponent_string = list(map(lambda m: m.name, opponent_board))
    player_board = minions[7:]
    player_string = list(map(lambda m: m.name, player_board))
    return tabulate([opponent_string, player_string], headers=[f"Pos. {i}" for i in range(1, 8)])


import os

clear = lambda: os.system('cls')


def read_log_file(filename: str):

    list_num = 0
    list_offset = 0
    minions = {}
    last_game_string = ''
    last_game_id = 0

    def my_filtering_function(pair):
        key, value = pair
        if value.list_id < last_game_id:
            return False  # keep pair in the filtered dictionary
        else:
            return True  # filter pair out of the dictionary

    for line_n in follow(open(filename, 'r')):
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
        games = []
        for list_id, minions_group in groupby(minions.values(), lambda minion: minion.list_id):
            try:
                minions_list_all = [minion for minion in list(minions_group)]
                minions_list = [minion for minion in minions_list_all if not minion.child_card]
                only_minions_list = [minion for minion in minions_list if not minion.spell]
                if len(only_minions_list) < 14:
                    continue
                only_minions_list.sort(key=atr('sort_key'))
                games.append(only_minions_list)
            except:
                pass
        if len(games) > 0:
            print_last = print_game(games[-1])
            if print_last != last_game_string:
                clear()
                print(print_last)
                last_game_string = print_last
                last_game_id = games[-1][0].list_id
        minions = dict(filter(my_filtering_function, minions.items()))
    return minions


WIN_LOG_PATH = 'C:\\Program Files (x86)\\Hearthstone\\Logs\\'
MAC_LOG_PATH = '/Applications/Hearthstone/Logs/'

if __name__ == '__main__':
    base_path = WIN_LOG_PATH if platform.system() == 'Windows' else MAC_LOG_PATH
    if not hs_running():
        print('Waiting for Hearthstone to start')
        hs_started = False
        while not hs_started:
            if hs_running():
                hs_started = True
            time.sleep(1)
        time.sleep(20)
    else:
        time.sleep(5)
    log_folders = list(os.listdir(base_path))
    log_folders.sort()
    current_log_folder = log_folders[-1]
    zone_exists = False
    log_path = os.path.join(base_path, current_log_folder, 'Zone.log')
    print(f"Current log path: {current_log_folder}")
    while not zone_exists:
        if os.path.exists(log_path):
            zone_exists = True
        time.sleep(1)
    print(f"Zone.log exists, starting reading")
    read_log_file(log_path)
