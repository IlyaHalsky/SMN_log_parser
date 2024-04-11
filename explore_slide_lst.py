from itertools import groupby
from operator import attrgetter as atr

from smn_game import Game
from smn_logs import read_log_file

def game_to_state(game):
    opponent = [m.attack_change for m in game.opponents_board]
    player = [m.attack_change for m in game.players_board]
    return [*opponent, *player]

def swap(state):
    swap = state[0]
    state[0] = state[7]
    state[7] = swap
    return state

def pipes(before, after):
    pipe = [0] * 14
    for i, ball in enumerate(before):
        pipe[i] = after.index(ball) + 1
    return pipe

if __name__ == '__main__':
    log_file = "Zone.log"
    log_path = log_file
    minions = read_log_file(log_path)
    log_name = log_file.rsplit('.', 1)[0]
    current_list = -1
    games = []
    for list_id, minions_group in groupby(minions.values(), lambda minion: minion.list_id):
        minions_list_all = [minion for minion in list(minions_group)]
        minions_list = [minion for minion in minions_list_all if not minion.child_card]
        only_minions_list = [minion for minion in minions_list if not minion.spell]
        if len(minions_list) < 14:
            continue

        only_minions_list.sort(key=atr('sort_key'))
        game = Game(only_minions_list, [])
        if not game.lst_complete:
            continue
        games.append(game)

    prev_game, *tail = games
    prev_state = game_to_state(prev_game)
    prev_state = swap(prev_state)
    all_pipes = []
    for current in tail:
        current_state = game_to_state(current)
        pipe = pipes(prev_state, current_state)
        all_pipes.append(pipe)
        prev_state = swap(current_state)
        break



