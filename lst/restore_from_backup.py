import json

from minions_utils import minions_by_id
from smn_game import Game
from smn_logs import Minion


def restore_minion(backup_name, board_id, minion_num, minion_dict) -> Minion:
    minion_id = minion_dict['card_id']
    minion_json = minions_by_id[minion_id]
    tags = []
    if minion_num < 7:
        tags.append(('CONTROLLER', '2 '))
    else:
        tags.append(('CONTROLLER', '1 '))
    tags.append(('ATK', f"{minion_dict['attack_total']} "))
    tags.append(('ZONE_POSITION', f'{minion_num % 7 + 1}'))
    minion_json['cost'] = minion_dict['mana_base']
    minion_json['attack'] = minion_dict['attack_base']
    minion_json['health'] = minion_dict['health_base']
    minion = Minion(
        backup_name,
        "unknown_date",
        board_id,
        board_id * 100 + minion_num,
        minion_dict['card_id'],
        minion_json['name'],
        [('RESTORED', '1'), *tags],
        [board_id]
    )
    minion.json = minion_json
    return minion


def restore_game(backup_name, game_dict) -> Game:
    minions_array = game_dict['minions']
    game_id = game_dict['game_id']
    minions = []
    for i, minion_dict in enumerate(minions_array):
        minions.append(restore_minion(backup_name, game_id, i, minion_dict))
    return Game(minions, [])


def restore_from_backup(backup_path) -> [Game]:
    games = []
    with open(backup_path, 'r') as f:
        backup_name = backup_path.split('/')[-1]
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            games.append(restore_game(backup_name, json.loads(line)))
    for game in games:
        assert len(set(game.attack_add)) == 14, f"{backup_path}, {game.attack_add}, {game}"
    return games


if __name__ == '__main__':
    path = "G:\\.shortcut-targets-by-id\\1CFpsGpqz65IlXdBeou1MB5lTdJbYxjv1\\Long Strange Trip runs\\Leftmost Attack Runs\\backup\\Halsky1.bkp"
    games = restore_from_backup(path)
    for game in games:
        assert len(set(game.attack_add)) == 14, f"{game.attack_add} {game}"
        print(game)
