import logging
import platform
import time
from itertools import groupby
from operator import attrgetter as atr
from typing import Iterator

import psutil
from tabulate import tabulate

from smn_game import Game
from smn_logs import extract_message, parse_minion
from utils import red, green

logging.basicConfig(filename='smn_helper.log', filemode='w', format='%(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


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

def color_spells(correct, spells):
    return list(map(lambda spell: red(spell.name) if spell.card_id not in correct else green(spell.name), spells))

def print_game(game: Game):
    opponent_string = list(map(lambda m: m.name, game.opponents_board))
    player_string = list(map(lambda m: m.name, game.players_board))
    # next_step = [game.next_step]
    correct_answers = [s.card_id for s in game.correct_smn_answers]
    spells_string1 = color_spells(correct_answers, game.spells[0:7])
    spells_string2 = color_spells(correct_answers, game.spells[7:14])
    spells_string3 = color_spells(correct_answers, game.spells[14:])
    return tabulate(
        [opponent_string, player_string, ["Spells:"], spells_string1, spells_string2, spells_string3],
        headers=[f"Pos. {i}" for i in range(1, 8)]
    )


def log_game(header: str, game: Game):
    logger.info(header)
    correct_answers = [s.card_id for s in game.correct_smn_answers]
    for i, minion in enumerate(game.opponents_board):
        logger.info(f"{minion.card_id}    ;O{i + 1};B{i + 1};H{correct_answers.index(minion.card_id) + 1};{minion.name}")
    for i, minion in enumerate(game.players_board):
        logger.info(
            f"{minion.card_id}    ;P{i + 1};B{i + 1 + 7};H{correct_answers.index(minion.card_id) + 1};{minion.name}"
        )


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
        carry_over = []
        for list_id, minions_group in groupby(minions.values(), lambda minion: minion.list_id):
            try:
                minions_list_all = [minion for minion in list(minions_group)]
                minions_list = [minion for minion in minions_list_all if not minion.child_card]
                only_minions_list = [minion for minion in minions_list if not minion.spell]
                only_spells_list = [minion for minion in minions_list if minion.spell]
                if len(only_minions_list) < 14 or len(only_spells_list) < 20:
                    if len(only_minions_list) > 0 and only_minions_list[-1].card_id == 'SCH_199':
                        carry_over = only_minions_list
                        continue
                    if len(carry_over) == 0:
                        continue
                    else:
                        only_minions_list = [*only_minions_list, *carry_over]
                        carry_over = []
                        if len(only_minions_list) != 14:
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

            print_last = print_game(last_game)
            print(f"Game: {list_offset // 100000 + 1} Turn: {list_num - 2}")
            print(print_last)
            #log_game(f"Game: {list_offset // 100000 + 1} Turn: {list_num - 2}", last_game)
            # image = create_board_image(last_game, 255 if has_dups else 0)
            # image = cv2.resize(image, (0, 0), fx=0.7, fy=0.7)
            # cv2.imshow('board', image)
            # cv2.waitKey(1)
        minions = dict(filter(my_filtering_function, minions.items()))
    return minions


if os.path.exists("config.txt"):
    with open('config.txt', 'r') as file:
        WIN_LOG_PATH = file.read()
else:
    WIN_LOG_PATH = 'C:\\Program Files (x86)\\Hearthstone\\Logs\\'
if os.path.exists("config.txt"):
    with open('config.txt', 'r') as file:
        MAC_LOG_PATH = file.read()
else:
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
