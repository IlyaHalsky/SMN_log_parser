import json

from smn_game import Game
from smn_logs import Minion


def backup_minion(minion: Minion):
    minion_dict = {
        'card_id': minion.card_id,
        'attack_add': minion.attack_change,
        'attack_total': minion.current_attack,
        'attack_base': minion.attack,
        'health_base': minion.health,
        'mana_base': minion.mana,
    }
    return minion_dict


def backup_game(game: Game):
    game_array = []
    for minion in game.minions:
        game_array.append(backup_minion(minion))
    return {
        "game_id": game.game_id,
        "game_offset": game.game_offset,
        "minions": game_array
    }


def backup_run(run):
    run_array = []
    for game in run.games:
        run_array.append(backup_game(game))
    return run_array


def save_run(filename: str, run):
    run_array = backup_run(run)
    with open(filename, 'w') as f:
        for game in run_array:
            f.write(json.dumps(game) + '\n')
