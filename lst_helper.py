import logging
import platform
import time
import json
import requests

from itertools import groupby
from operator import attrgetter as atr
from typing import Iterator

import psutil
from tabulate import tabulate

from smn_game import Game
from smn_logs import extract_message, parse_minion

logging.basicConfig(filename='lst_helper.log', filemode='a', format='%(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.WARNING)  # Or logging.ERROR to suppress further
logging.getLogger("requests").setLevel(logging.WARNING)


def hs_running():
    for pid in psutil.pids():
        if psutil.pid_exists(pid):
            try:
                if 'Hearthstone' in psutil.Process(pid).name():
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


# def print_game(game: Game, log_format: bool, initial_map):
#    #opponent_string = list(map(lambda m: str(m.attack_change), game.opponents_board))
#    #player_string = list(map(lambda m: str(m.attack_change), game.players_board))
#    opponent_string = list(map(lambda m: f"{initial_map[m.attack_change]}({m.attack_change})", game.opponents_board))
#    player_string = list(map(lambda m: f"{initial_map[m.attack_change]}({m.attack_change})", game.players_board))
#    if log_format:
#        return f"{','.join(opponent_string)}\n{','.join(player_string)}"
#    else:
#        return tabulate([opponent_string, player_string], headers=[f"Pos. {i}" for i in range(1, 8)])

def solution(opponent, player):
    o_s = sum(opponent)
    p_s = sum(player)
    best_diff = abs(o_s - p_s)
    best_move = [-1,-1, -1, -1, -1, -1]
    for i, o in enumerate(opponent):
        for j, p in enumerate(player):
            o_n = o_s - o + p
            p_n = p_s - p + o
            diff = abs(o_n - p_n)
            if diff <= best_diff:
                best_move = [p, o, j + 1, i + 1, p_n, o_n]
                best_diff = diff
    return best_move, best_diff

def print_game(game: Game, log_format: bool, json_format: bool):
    opponent_string = list(map(lambda m: str(m.attack_change), game.opponents_board))
    player_string = list(map(lambda m: str(m.attack_change), game.players_board))
    #possible_moves = []
    #for o_a in [m.attack_change for m in game.opponents_board]:
    #    for p_a in [m.attack_change for m in game.players_board]:
    #        if (p_a, o_a) in moves_needed:
    #            possible_moves.append((p_a, o_a))
    #possible_moves.sort(key=lambda a: a[0])
    #opp_sum = sum(map(lambda m: m.attack_change, game.opponents_board))
    #player_sum = sum(map(lambda m: m.attack_change, game.players_board))
    #best_move, best_diff = solution(list(map(lambda m: m.attack_change, game.opponents_board)), list(map(lambda m: m.attack_change, game.players_board)))
    #[p_a, o_a, p_p, o_p, p_s, o_s] = best_move
    #move = ["Pos.",f"{p_p}->{o_p}", "Attack", f"{p_a}->{o_a}",  "Summs:" ,f"P: {p_s} O:{o_s}"]
    #possible_moves_str = [str(a) for a in possible_moves]
    if json_format:
        output_list = opponent_string + player_string
        return list(map(int, output_list)) # Convert strings to integers
        # F-string will add the brackets
    if log_format:
        return f"{','.join(opponent_string)}\n{','.join(player_string)}"
    else:
        return tabulate(
            [
                opponent_string,
                player_string,
                #possible_moves_str
                #["Player", player_sum, "Opponent", opp_sum],
                #["Difference", player_sum - opp_sum],
                #move,
                #["Best Difference", best_diff],
            ], headers=[f"Pos. {i}" for i in range(1, 8)]
        )


import os

if platform.system() == 'Windows':
    clear = lambda: os.system('cls')
else:
    clear = lambda: os.system('clear')


def read_log_file(filename: str):
    logger.info(f"Logfile {filename}")
    list_num = 0
    list_offset = 0
    minions = {}

    def my_filtering_function(pair):
        key, value = pair
        if last_game is not None and value.list_id < last_game.list_id - 5:
            return False  # keep pair in the filtered dictionary
        else:
            return True  # filter pair out of the dictionary

    last_game = None
    last_game_hash = ''
    # initial_map = {}
    # first_game = -1

    for line_n in follow(open(filename, 'r')):
        line = line_n[:-1]
        # print(line)
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
                if len(only_minions_list) != 14:
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
                only_minions_list.sort(key=atr('sort_key'))
                current_game = Game(only_minions_list, [])
                # if list_offset > first_game and current_game.lst_complete:
                #    first_game = list_offset
                #    initial_map = {}
                #    for i, opp in enumerate(current_game.opponents_board):
                #        initial_map[opp.attack_change] = i + 1
                #    for j, pl in enumerate(current_game.players_board):
                #        initial_map[pl.attack_change] = j + 1 + 7

                # print(current_game)
            except:
                pass
        if current_game is not None and last_game_hash != current_game.hash_lst and current_game.lst_complete:
            clear()
            last_game = current_game
            last_game_hash = last_game.hash_lst
            print_last = print_game(last_game, True, False)
            print_json = print_game(last_game, False, True)
            print(f"Game: {list_offset // 100000 + 1} Turn: {list_num - 2}")
            print(print_last)
            print(print_json)

            logger.info(f"Game: {list_offset // 100000 + 1} Turn: {list_num - 2}")
            logger.info(print_last)

            #TODO: Add the minions in this too.
            data = {
                "Game": list_offset // 100000 + 1,
                "Turn": list_num - 2,
                "board": print_game(last_game, True, True)
            }

            url = 'http://155.138.193.23/upload'
            response = requests.post(url, json=data)

            #logger.info(f"Game: {list_offset // 100000 + 1}, Turn: {list_num - 2}")
            #logger.info(print_game(last_game, True, False))
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
        read_log_file('Zone.log')
