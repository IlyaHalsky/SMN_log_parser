import platform
import time
from collections import defaultdict
from dataclasses import dataclass
from itertools import groupby
from operator import attrgetter as atr
from typing import Iterator, List

import cv2
import psutil
from playsound import playsound
from tabulate import tabulate

from smn_game import Game
from smn_logs import extract_message, parse_minion, Minion, minions_by_id, resource_path
from visualize import create_board_image


def hs_running():
    for pid in psutil.pids():
        if psutil.pid_exists(pid):
            try:
                if 'Hearthstone.exe' in psutil.Process(pid).name():
                    return True
            except:
                pass
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



def print_game(game: Game):
    opponent_string = list(map(lambda m: m.name, game.opponents_board))
    player_string = list(map(lambda m: m.name, game.players_board))
    #next_step = [game.next_step]
    spells_string1 = list(map(lambda m: m.name, game.spells[0:8]))
    spells_string2 = list(map(lambda m: m.name, game.spells[8:15]))
    spells_string3 = list(map(lambda m: m.name, game.spells[15:]))
    return tabulate([opponent_string, player_string, ["Spells:"], spells_string1, spells_string2, spells_string3], headers=[f"Pos. {i}" for i in range(1, 8)])


import os

clear = lambda: os.system('cls')


def read_log_file(filename: str):

    list_num = 0
    list_offset = 0
    minions = {}

    def my_filtering_function(pair):
        key, value = pair
        if last_game is not None and value.list_id < last_game.list_id:
            return False  # keep pair in the filtered dictionary
        else:
            return True  # filter pair out of the dictionary

    last_game = None
    last_game_hash = ''
    for line_n in follow(open(filename, 'r')):
        line = line_n[:-1]
        date, type, message = extract_message(line)
        if type == 'list-start':
            if message >= list_num:
                list_num = message
            else:
                list_offset = list_offset + 100000
                list_num = message
        if type == 'list-item':
            parse_minion(date, filename, message, minions, list_offset)

        current_game = None
        for list_id, minions_group in groupby(minions.values(), lambda minion: minion.list_id):
            try:
                minions_list_all = [minion for minion in list(minions_group)]
                minions_list = [minion for minion in minions_list_all if not minion.child_card]
                only_minions_list = [minion for minion in minions_list if not minion.spell]
                only_spells_list = [minion for minion in minions_list if minion.spell]
                if len(only_minions_list) < 14 or len(only_spells_list) < 20:
                    continue
                if any([spell.name == '???' for spell in only_spells_list]):
                    continue
                only_minions_list.sort(key=atr('sort_key'))
                only_spells_list.sort(key=atr('sort_key_safe'))
                current_game = Game(only_minions_list, only_spells_list)
            except:
                pass
        if current_game is not None and last_game_hash != current_game.hash:
            clear()
            last_game = current_game
            last_game_hash = last_game.hash

            has_dups = False
            group_by = lambda card: card.card_id
            grouped = defaultdict(list)
            for spell in last_game.spells:
                grouped[group_by(spell)].append(spell)
            for key, value in grouped.items():
                if len(value) > 1:
                    print(f"Duplicate, POG: {key} {minions_by_id[key]['name']}")
                    print(f"Duplicate, POG: {key} {minions_by_id[key]['name']}")
                    for card in value:
                        card.color[1] = 255
                    for minion in last_game.minions:
                        if group_by(minion) == key:
                            minion.color[1] = 255
                    has_dups = True
            print_last = print_game(last_game)

            print(print_last)
            if not has_dups:
                print("Keep on panning!")
                #playsound(resource_path("rich.wav"))
            else:
                print("Hoowee, I'm rich!")
                playsound(resource_path("rich.wav"))
            #image = create_board_image(last_game, 255 if has_dups else 0)
            #image = cv2.resize(image, (0, 0), fx=0.7, fy=0.7)
            #cv2.imshow('board', image)
            #cv2.waitKey(1)
        minions = dict(filter(my_filtering_function, minions.items()))
    return minions

if os.path.exists("config.txt"):
    with open('config.txt', 'r') as file:
        WIN_LOG_PATH = file.read()
else:
    WIN_LOG_PATH = 'C:\\Program Files (x86)\\Hearthstone\\Logs\\'
MAC_LOG_PATH = '/Applications/Hearthstone/Logs/'

if __name__ == '__main__':
    debug = False
    if not debug:
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
    else:
        read_log_file('logs/Zone.log')
