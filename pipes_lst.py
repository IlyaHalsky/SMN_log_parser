import os
from collections import defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
from itertools import groupby
from operator import attrgetter as atr

from tqdm import tqdm

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

    @property
    def pipe_key(self):
        return ','.join(map(str, self.pipe))

    def changed_into(self, ball: Ball):
        initial_index = self.before.index(ball)
        next_position = self.pipe[initial_index]
        return self.after[next_position]

    def next_position(self, ball: Ball):
        initial_index = self.before.index(ball)
        next_position = self.pipe[initial_index]
        return next_position


def track_ball(minion_pos: int, start: State, pipes: [Pipe]) -> [Ball]:
    tracking = start.balls[minion_pos]
    trip = [tracking]
    for pipe in pipes:
        tracking = pipe.changed_into(tracking)
        trip.append(tracking)
    return trip


def track_position(minion_pos: int, start: State, pipes: [Pipe]) -> [int]:
    tracking = start.balls[minion_pos]
    trip = [minion_pos]
    for pipe in pipes:
        trip.append(pipe.next_position(tracking))
        tracking = pipe.changed_into(tracking)
    return trip


s = SequenceMatcher()


def longest_common(list1, list2):
    s.set_seqs(list1, list2)
    a, b, size = s.find_longest_match()
    return list1[a:a + size], a, b, size


if __name__ == '__main__':
    log_folder = "G:\\.shortcut-targets-by-id\\1CFpsGpqz65IlXdBeou1MB5lTdJbYxjv1\\Long Strange Trip runs\\Leftmost Attack Runs"
    all_pipes = []
    all_trips = []
    for log_file in tqdm(os.listdir(log_folder)):
        log_path = os.path.join(log_folder, log_file)
        if os.path.isdir(log_path):
            continue
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
        prev_state = first_state
        # prev_state = prev_state.do_attack(1, 1)
        current_pipes = []
        # print(prev_state.attack_changes)
        for current in tail:
            current_state = State.from_game(current)
            pipe = Pipe(prev_state, current_state)
            current_pipes.append(pipe)
            # print(','.join([str(i + 1) for i in pipe.pipe]))
            # prev_state = current_state.do_attack(1, 1)
            prev_state = current_state
        all_pipes.extend(current_pipes)
        break
        # for i in range(14):
        #    #trip = track_ball(i, first_state, current_pipes)
        #    #trip_names = []
        #    #for ball in trip:
        #    #    trip_names.append(ball.minion_id)
        #    #all_trips.append(trip_names)
        #    trip = track_position(i, first_state, current_pipes)
        #    all_trips.append((trip, log_name, i))
        #    #if os.path.exists(f"trip/{i}"):
        #    #    shutil.rmtree(f"trip/{i}")
        #    #os.makedirs(f"trip/{i}")
        #    #for j, ball in enumerate(trip):
        #    #    print(j, ball)
        #    #    shutil.copy(f"image_cache/{ball.minion_id}.png", f"trip/{i}/{j}.png")

    for key, value in groupby(all_pipes, lambda pipe: pipe.pipe_key):
        pipes = list(value)
        if len(pipes) > 1:
            print(key, pipes)

    commons = []
    for i in tqdm(range(len(all_trips)), desc='Trip Longest Common'):
        trip1, name1, i1 = all_trips[i]
        for j in range(i + 1, len(all_trips)):
            trip2, name2, i2 = all_trips[j]
            common, a, b, size = longest_common(trip1, trip2)
            commons.append((common, size, (a, b), (name1, name2), (i1, i2)))
    commons.sort(key=lambda x: x[1], reverse=True)
    for common, size, start, names, iis in commons:
        if size > 5:
            print(common, size, start, names, iis)

    group_pipes = defaultdict(list)
    for pipe in all_pipes:
        before = pipe.before
        group_pipes[(before[0].attack_change, before[7].attack_change)].append(pipe)

    for key, value in group_pipes.items():
        if len(value) > 1:
            print(key)
            for v in value:
                print(v.before.attack_changes, v.pipe, v.after.attack_changes)
