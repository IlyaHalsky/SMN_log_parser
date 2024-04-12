from _operator import attrgetter as atr
from dataclasses import dataclass
from hashlib import sha256
from typing import List

from smn_logs import Minion


@dataclass
class Game:
    minions: List[Minion]
    spells: List[Minion]

    @property
    def opponents_board(self) -> List[Minion]:
        return list(self.minions[:7])

    @property
    def players_board(self) -> List[Minion]:
        return list(self.minions[7:])

    @property
    def list_id(self):
        return self.minions[0].list_id

    @property
    def opponents_board_current(self) -> List[Minion]:
        return list(filter(lambda x: x.shown, self.minions[:7]))

    @property
    def players_board_current(self) -> List[Minion]:
        return list(filter(lambda x: not x.last_set_aside, self.minions[7:]))

    @property
    def known_spells(self):
        return list(filter(lambda spell: spell.name != '???', self.spells))

    @property
    def unknown_spells(self):
        return list(filter(lambda spell: spell.name == '???', self.spells))

    @property
    def current_spells(self) -> List[Minion]:
        return list(filter(lambda spell: not spell.used, self.spells))

    @property
    def hash(self) -> str:
        all_cards = [*self.minions, *self.spells]
        all_ids = list(map(lambda minion: minion.card_id, all_cards))
        all_ids_concat = ';'.join(all_ids)
        return sha256(all_ids_concat.encode()).hexdigest()

    @property
    def hash_lst(self) -> str:
        all_cards = [*self.minions, *self.spells]
        all_ids = list(map(lambda minion: f"{minion.card_id}/{minion.attack_change}", all_cards))
        all_ids_concat = ';'.join(all_ids)
        return sha256(all_ids_concat.encode()).hexdigest()

    @property
    def lst_complete(self) -> bool:
        return all([minion.current_attack is not None for minion in self.minions])

    @property
    def left_out_current(self):
        lo = []
        self.minions.sort(key=atr('sort_key'))
        self.spells.sort(key=atr('position_safe'))
        for i, spell in enumerate(self.spells):
            solved = False
            for j, minion in enumerate(self.minions):
                if spell.card_id == minion.card_id:
                    solved = True
                    break
            if not solved:
                lo.append(spell)
        return list(filter(lambda m: len(m.json) != 0, lo))

    @property
    def next_step(self):
        opponents = self.opponents_board_current
        players = self.players_board_current
        spells = self.current_spells
        spells.sort(key=atr('position_safe'))
        for j, spell in enumerate(spells):
            s_card_id = spell.card_id
            for i, opponent in enumerate(opponents):
                if opponent.card_id == s_card_id:
                    return f"{spell.name}: Spell {j + 1} -> Opponent {i + 1}"
            for i, player in enumerate(players):
                if player.card_id == s_card_id:
                    return f"{spell.name}: Spell {j + 1} -> Player {i + 1}"

    def __post_init__(self):
        self.correct = ['  0'] * len(self.spells)
        self.position = [' -1'] * len(self.spells)
        self.used = []
        self.left_out = []
        self.minions.sort(key=atr('sort_key'))
        self.spells.sort(key=atr('position'))
        for i, spell in enumerate(self.spells):
            solved = False
            for j, minion in enumerate(self.minions):
                if spell.card_id == minion.card_id:
                    self.correct[i] = '  ' + str(1)
                    self.position[i] = str(j).rjust(3)
                    self.used.append(minion)
                    solved = True
                    break
            if not solved:
                self.left_out.append(spell)
                spell.color[2] = 255
            else:
                spell.color[2] = 0

    @property
    def game_id(self):
        return max(list(map(lambda x: x.list_id, self.minions)))
