import json

from lst.lst_config import LSTConfig
from smn_game import Game


def upload_game(game: Game, config: LSTConfig):
    game_dict = {
        'player': '???',
        'timestamp': 0,
        'game_id': 0,
        'turn': 0,
        'added_attack': game.attack_add,
        'minion_ids': [minion.card_id for minion in game.minions],
        'attacker': game.attacker.attack_change,
        'defender': game.defender.defender_change,
    }
    game_json = json.dumps(game_dict)
    '''
    #TODO: Add the minions in this too.
    data = {
        "Game": list_offset // 100000 + 1,
        "Turn": list_num - 2,
        "board": print_game(last_game, True, True)
    }

    url = 'http://155.138.193.23/upload'
    response = requests.post(url, json=game_json)
    '''