import os
from _operator import attrgetter as atr
from dataclasses import dataclass
from itertools import groupby

from tqdm import tqdm

from lst.backup_game import save_run
from lst.restore_from_backup import restore_from_backup
from smn_game import Game
from smn_logs import read_log_file


@dataclass
class Run:
    full_path: str
    log_name: str
    games: [Game]

    @property
    def last_offset_games(self) -> [Game]:
        current_offset = 0
        games = []
        for game in self.games:
            if current_offset != game.game_offset:
                current_offset = game.game_offset
                games = []
            games.append(game)
        return games


@dataclass
class Runs:
    runs: [Run]

    def __post_init__(self):
        self.all_games = [game for run in self.runs for game in run.games]


def find_backup(logs_path, log_file):
    backup_name = log_file.replace('.log', '') + '.bkp'
    backup_path = os.path.join(logs_path, 'backup', backup_name)
    if os.path.exists(backup_path):
        return backup_path
    else:
        return None


def read_all_games(logs_path, log_names=None):
    if log_names is None:
        log_names = []
    runs = []
    if not os.path.exists(logs_path + "\\backup"):
        os.mkdir(logs_path + "\\backup")

    for log_file in tqdm(os.listdir(logs_path), desc="Reading Zone logs"):
        log_path = os.path.join(logs_path, log_file)
        if os.path.isdir(log_path):
            continue
        if log_file not in log_names and len(log_names) != 0:
            continue
        if not log_file.endswith('.log'):
            continue

        if (backup_path := find_backup(logs_path, log_file)) is not None:
            current_games = restore_from_backup(backup_path)
            runs.append(Run(log_path, log_file, current_games))
        else:
            current_games = []
            minions = read_log_file(log_path)

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
                assert len(set(game.attack_add)) == 14, str(game.attack_add) + log_file + str(game)
                if not game.lst_complete:
                    continue
                current_games.append(game)
            run = Run(log_path, log_file, current_games)

            backup_name = run.log_name
            save_path = logs_path + "\\" + "backup\\" + backup_name.replace(".log", "") + ".bkp"
            save_run(save_path, run)
            runs.append(run)
    return Runs(runs)
