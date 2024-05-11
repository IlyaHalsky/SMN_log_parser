import logging
import os
import time
import traceback
from itertools import groupby
from operator import attrgetter as atr

from tabulate import tabulate, SEPARATING_LINE

from helper_utils import clear_console, hs_running, follow_file
from lst.lst_config import read_config, LSTConfig
from smn_game import Game
from smn_logs import extract_message, parse_minion, RESTART_OFFSET, Minion
from utils import yellow, red, cyan, colorize


def get_minions_string(attack_add_colors, minions: [Minion], config: LSTConfig):
    result = []
    for i, minion in enumerate(minions):
        minion_strings = []
        if config.show_attack_add:
            if minion.attack_change in attack_add_colors:
                minion_strings.append(colorize(minion.attack_change, attack_add_colors[minion.attack_change]))
            else:
                minion_strings.append(minion.attack_change)
        if config.show_attack_full:
            minion_strings.append(minion.current_attack)
        if config.show_attack_base:
            minion_strings.append(yellow(minion.attack))
        if config.show_health:
            minion_strings.append(red(minion.health))
        if config.show_mana:
            minion_strings.append(cyan(minion.mana))
        if config.show_minion_name:
            minion_strings.append(minion.name)
        if config.show_set:
            minion_strings.append(minion.expansion)
        if config.show_sub_set:
            minion_strings.append(get_miniset(minion))
        if config.show_minion_id:
            minion_strings.append(minion.card_id)
        result.append(' '.join(map(str, minion_strings)))
    return result

def find_loops(game: Game):
    attack_add = game.attack_add
    used = set()
    loops = []
    for i, attack in enumerate(game.attack_add):
        if attack not in used:
            loop = [attack]
            used.add(attack)
            next_ind = attack - 1
            while attack_add[next_ind] not in used:
                current_value = attack_add[next_ind]
                loop.append(current_value)
                used.add(current_value)
                next_ind = current_value - 1
            loops.append(loop)
    highlight = {}
    for i, loop in enumerate(loops):
        for attack in loop:
            highlight[attack] = i
    return highlight

def get_miniset(minion):
    if minion.expansion_raw == 'LEGACY' or minion.expansion_raw == 'EXPERT1':
        return 'LEGACY'
    else:
        return minion.card_id.split('_')[0]

def find_matching_sub_sets(game: Game):
    opponent_sets = set([get_miniset(m) for m in game.opponents_board])
    player_sets = set([get_miniset(m) for m in game.players_board])
    overlap = list(opponent_sets & player_sets)
    highlight = {}
    for m in game.minions:
        if get_miniset(m) in overlap:
            highlight[m.attack_change] = overlap.index(get_miniset(m)) + 1
    return highlight

def get_minions_strings(game: Game, config: LSTConfig):
    if config.paint_color_cycles:
        attack_add_colors = find_loops(game)
    elif config.paint_matching_sub_sets:
        attack_add_colors = find_matching_sub_sets(game)
    else:
        attack_add_colors = {}
    opponent_string = get_minions_string(attack_add_colors, game.opponents_board, config)
    player_string = get_minions_string(attack_add_colors, game.players_board, config)
    return opponent_string, player_string

def find_opposite(game: Game):
    opponent = game.attack_add[:7]
    player = game.attack_add[7:]
    for i in range(1, 8):
        if i in player and (15 - i) in opponent:
            return f"{i} -> {15 - i}"
        if i in opponent and (15 - i) in player:
            return f"{15 - i} -> {i}"
    return ""

def print_paint(game: Game, config: LSTConfig):
    if config.paint_attack_sum_15:
        opposite = find_opposite(game)
        print(opposite)

def print_game(header: str, game: Game, config: LSTConfig):
    opponent_string, player_string = get_minions_strings(game, config)
    print(header)
    print(
        tabulate(
            [
                opponent_string,
                player_string,
                SEPARATING_LINE,
                [f"Pos. {i}" for i in range(8, 15)]
            ], headers=[f"Pos. {i}" for i in range(1, 8)]
        )
    )
    print_paint(game, config)


def get_minions_log(minions, config: LSTConfig):
    result = []
    for i, minion in enumerate(minions):
        minion_strings = []
        if config.log_attack_add:
            minion_strings.append(minion.attack_change)
        if config.log_attack_full:
            minion_strings.append(minion.current_attack)
        if config.log_attack_base:
            minion_strings.append(minion.attack)
        if config.log_health:
            minion_strings.append(minion.health)
        if config.log_mana:
            minion_strings.append(minion.mana)
        if config.log_minion_id:
            minion_strings.append(minion.card_id)
        if config.log_set:
            minion_strings.append(minion.expansion_raw)
        result.append(minion_strings)
    return list(zip(*result))


def combine_minions(minion_strings, config: LSTConfig):
    return config.log_type_seperator.join(
        [config.log_array_separator.join(map(str, minions)) for minions in minion_strings]
    )


def get_attack_log(game: Game, config: LSTConfig):
    return f"{game.attacker.attack_change}{config.log_array_separator}{game.defender.attack_change}"


def log_game(header, game: Game, logger, config: LSTConfig):
    opponent_strings = get_minions_log(game.opponents_board, config)
    player_strings = get_minions_log(game.players_board, config)
    logger.info(header)
    logger.info(combine_minions(opponent_strings, config))
    logger.info(combine_minions(player_strings, config))
    if game.attacker is not None and game.defender is not None:
        logger.info(get_attack_log(game, config))


def read_log_file(filename: str, logger, config):
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

    for line_n in follow_file(open(filename, 'r')):
        line = line_n[:-1]
        date, type, message = extract_message(line)
        if type == 'list-start':
            if message >= list_num:
                list_num = message
            else:
                list_offset = list_offset + RESTART_OFFSET
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
            except:
                pass

        if current_game is not None and last_game_hash != current_game.hash_lst and current_game.lst_complete:
            clear_console()
            last_game = current_game
            last_game_hash = last_game.hash_lst
            header = f"Game: {list_offset // RESTART_OFFSET + 1} Turn: {list_num - 2}"
            print_game(header, last_game, config)
            log_game(header, last_game, logger, config)
        minions = dict(filter(my_filtering_function, minions.items()))
    return minions


if __name__ == '__main__':
    try:
        config = read_config()
        print(config.to_print())
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
        log_folders = [folder for folder in os.listdir(config.hs_logs_path) if 'Hearthstone_' in folder]
        log_folders.sort()
        current_log_folder = log_folders[-1]
        log_date = current_log_folder.replace('Hearthstone_', '')
        zone_exists = False
        log_path = os.path.join(config.hs_logs_path, current_log_folder, 'Zone.log')
        print(f"Current log path: {current_log_folder}")
        logging.basicConfig(filename=f'lst_{log_date}.log', filemode='w', format='%(message)s')
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        while not zone_exists:
            if os.path.exists(log_path):
                zone_exists = True
            time.sleep(1)
        print(f"Zone.log exists, starting reading")
        read_log_file(log_path, logger, config)
    except Exception as e:
        traceback.print_exc()
        with open("./lst_helper_crash.txt", "w") as crashLog:
            crashLog.write(traceback.format_exc())
