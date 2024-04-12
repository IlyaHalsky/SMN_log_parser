import os
import shutil
from dataclasses import dataclass
from itertools import groupby
from operator import attrgetter as atr

from smn_game import Game
from smn_logs import read_log_file, Minion


@dataclass
class Ball:
    attack_change: int
    minion_id: str

    @staticmethod
    def from_minion(minion: Minion):
        return Ball(minion.attack_change, minion.card_id)


@dataclass
class State:
    balls: [Ball]

    def __getitem__(self, i):
        return self.balls[i]

    def index(self, ball: Ball) -> int:
        return self.balls.index(ball)

    def do_attack(self, player_position: int, opponent_position: int) -> 'State':
        balls = self.balls.copy()
        swap = balls[opponent_position - 1]
        balls[opponent_position - 1] = balls[player_position - 1 + 7]
        balls[player_position - 1 + 7] = swap
        return State(balls)

    @staticmethod
    def from_game(game: Game) -> 'State':
        opponent = [Ball.from_minion(minion) for minion in game.opponents_board]
        player = [Ball.from_minion(minion) for minion in game.players_board]
        return State([*opponent, *player])

    @property
    def attack_changes(self):
        return [ball.attack_change for ball in self.balls]


@dataclass
class Pipe:
    before: State
    after: State

    def __post_init__(self):
        self.pipe = [0] * 14
        for i, ball_before in enumerate(self.before.balls):
            for j, ball_after in enumerate(self.after.balls):
                if ball_before.attack_change == ball_after.attack_change:
                    self.pipe[i] = j
                    break

    def changed_into(self, ball: Ball):
        initial_index = self.before.index(ball)
        next_position = self.pipe[initial_index]
        return self.after[next_position]


def track_minion(minion_id: int, start: State, pipes: [Pipe]):
    tracking = start.balls[minion_id]
    trip = [tracking]
    for pipe in pipes:
        tracking = pipe.changed_into(tracking)
        trip.append(tracking)
    return trip


if __name__ == '__main__':
    log_file = "G:\\.shortcut-targets-by-id\\1CFpsGpqz65IlXdBeou1MB5lTdJbYxjv1\\Long Strange Trip runs\\Leftmost Attack Runs\\Halsky1.log"
    log_path = log_file
    minions = read_log_file(log_path)
    log_name = log_file.rsplit('.', 1)[0]
    current_list = -1
    games = []

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
        games.append(game)

    first_game, *tail = games
    first_state = State.from_game(first_game)
    prev_state = first_state.do_attack(1, 1)
    #print(prev_state.attack_changes)
    all_pipes = []
    for current in tail:
        current_state = State.from_game(current)
        pipe = Pipe(prev_state, current_state)
        all_pipes.append(pipe)
        print(','.join([str(i + 1) for i in pipe.pipe]))
        prev_state = current_state.do_attack(1, 1)

    #for i in range(14):
    #    trip = track_minion(i, first_state, all_pipes)
    #    if os.path.exists(f"trip/{i}"):
    #        shutil.rmtree(f"trip/{i}")
    #    os.makedirs(f"trip/{i}")
    #    for j, ball in enumerate(trip):
    #        print(j, ball)
    #        shutil.copy(f"image_cache/{ball.minion_id}.png", f"trip/{i}/{j}.png")
