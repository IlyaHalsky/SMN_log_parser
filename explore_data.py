import os
import platform
import re
from collections import deque, defaultdict
from dataclasses import dataclass
from itertools import groupby
from typing import List
from operator import methodcaller as mc
from operator import attrgetter as atr

from smn_logs import WIN_LOG_PATH, MAC_LOG_PATH, extract_message, parse_minion, read_log_file, Minion


@dataclass
class Game:
    minions: List[Minion]
    spells: List[Minion]

    def __post_init__(self):
        self.correct = ['  0']*len(self.spells)
        self.position = [' -1']*len(self.spells)
        self.used = []
        self.left_out = []
        self.minions.sort(key=atr('sort_key'))
        self.spells.sort(key=atr('position'))
        for i, spell in enumerate(self.spells):
            solved = False
            for j, minion in enumerate(self.minions):
                if spell.name == minion.name:
                    self.correct[i] = '  ' + str(1)
                    self.position[i] = str(j).rjust(3)
                    self.used.append(minion)
                    solved = True
                    break
            if not solved:
                self.left_out.append(spell)

    def __repr__(self):
        return f'{''.join(self.correct)} {''.join(self.position)}'

    @property
    def game_id(self):
        return max(list(map(lambda x: x.list_id, self.minions)))

def largest_substring_algo1(seq):
    l = list(seq)
    d = deque(seq[1:])
    match = []
    longest_match = []
    while d:
        for i, item in enumerate(d):
            if l[i]==item:
                match.append(item)
            else:
                if len(longest_match) < len(match):
                    longest_match = match
                match = []
        d.popleft()
    return longest_match

if __name__ == '__main__':
    logs_path = "logs"
    for log_file in os.listdir(logs_path):
        log_path = os.path.join(logs_path, log_file)
        minions = read_log_file(log_path)
        current_list = -1
        minions_seq = ''
        for list_id, minions_group in groupby(minions.values(), lambda minion: minion.list_id):
            minions_list_all = [minion for minion in list(minions_group)]
            minions_list = [minion for minion in minions_list_all if not minion.child_card]
            only_minions_list = [minion for minion in minions_list if not minion.spell]
            only_spells_list = [minion for minion in minions_list if minion.spell]
            if len(minions_list) < 34:
                continue
            if any([spell.name == '???' for spell in only_spells_list]):
                continue
            minions_list.sort(key=lambda minion: minion.id)
            game = Game(only_minions_list, only_spells_list)
            minions_seq = minions_seq + ''.join(game.position).replace(' ', '')
        print(largest_substring_algo1(list(minions_seq)))


