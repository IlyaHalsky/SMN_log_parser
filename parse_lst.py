import os
from _operator import attrgetter as atr
from dataclasses import dataclass
from itertools import groupby

from tqdm import tqdm

from smn_game import Game
from smn_logs import read_log_file


@dataclass
class Run:
    games: [Game]


@dataclass
class Runs:
    runs: [Run]

    def __post_init__(self):
        self.all_games = [game for run in self.runs for game in run.games]


def read_all_games(logs_path):
    runs = []
    for log_file in tqdm(os.listdir(logs_path)):
        log_path = os.path.join(logs_path, log_file)
        if os.path.isdir(log_path):
            continue
        minions = read_log_file(log_path)

        current_games = []
        carry_over = []
        for list_id, minions_group in groupby(minions.values(), lambda minion: minion.list_id):
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
            game = Game(only_minions_list, [])
            if not game.lst_complete:
                continue
            current_games.append(game)
        runs.append(Run(current_games))
    return Runs(runs)


