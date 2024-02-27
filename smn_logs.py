import json
import os
import platform
import re
import sys
from dataclasses import dataclass
from itertools import groupby

from hearthstone.enums import CardSet

from card_sets import set_names

TIMESTAMP_RE = re.compile(r"^([DWE]) ([\d:.]+) (.+)$")
MESSAGE_RE = re.compile(r"^(.*) - (.*)$")
LIST_START = re.compile(r"ZoneMgr.AddServerZoneChanges\(\) - taskListId=(\d*) changeListId=(\d*)")
LIST_ITEM = re.compile(r"ZoneMgr.AddServerZoneChanges\(\) - AddChange\(\) (changeList.*)")
LIST_END = re.compile(r"ZoneChangeList.Finish\(\) - id=(\d*)")


def extract_message(log_line):
    if log_line is None:
        return None, None
    message = TIMESTAMP_RE.match(log_line).group(3)
    if message is None:
        return None, None
    if LIST_START.match(message):
        return "list-start", int(LIST_START.match(message).group(2))
    if LIST_ITEM.match(message):
        return "list-item", LIST_ITEM.match(message).group(1)
    if LIST_END.match(message):
        return "list-end", int(LIST_END.match(message).group(1))
    return None, None

import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
minions_json = json.load(open(resource_path('cards.collectible.json'), encoding="utf8"))
minions_by_id = {card['id']: card for card in minions_json if card['type'] == 'MINION'}
minions_by_name = {card['name']: card for card in minions_json if card['type'] == 'MINION'}


def parse_minion(log, minions, list_offset):
    change_list_match = re.match(
        r'changeList: id=(\d+)', log
    )
    list_id = int(change_list_match.group(1)) + list_offset
    match = re.search(r'\[id=(\d+) cardId=(.*?) name=(.*?)\]', log)
    if match:
        minion_id = int(match.group(1)) + list_offset
        card_id = match.group(2)
        name = match.group(3)
        if minion_id not in minions:
            minions[minion_id] = Minion(
                list_id=list_id,
                id=minion_id,
                card_id=card_id,
                name=name,
                tags=[],
                lists=[list_id],
                json=minions_by_id.get(card_id, {}),
            )
        elif minions[minion_id].name == '???':
            minions[minion_id].name = name
        tags = re.search(r'\[type=TAG_CHANGE.*tag=(.*?) value=(.*?)\]', log)
        if tags:
            minions[minion_id].tags.append((tags.group(1), tags.group(2)))
            minions[minion_id].lists.append(list_id)
    return None


@dataclass
class Minion:
    list_id: int
    id: int
    card_id: str
    name: str
    tags: []
    lists: []
    json: {}
    spell: bool = False

    def __post_init__(self):
        self.spell = self.name == '???'

    # def __repr__(self):
    #    player = 'O' if ('CONTROLLER', '2 ') in self.tags else 'P'
    #    position = next((tag[1] for tag in self.tags if tag[0] == 'ZONE_POSITION'), '')
    #    tpe = 'S' if self.spell else 'M'
    #    return f'{tpe}|{self.name}|{player}:{position}'

    @property
    def child_card(self):
        return any(tag[0] == 'PARENT_CARD' for tag in self.tags)

    @property
    def player(self):
        return 0 if ('CONTROLLER', '2 ') in self.tags else 1

    @property
    def position(self):
        return int(next((tag[1] for tag in self.tags if tag[0] == 'ZONE_POSITION'))) - 1

    @property
    def sort_key(self):
        return (self.player, self.position)

    @property
    def expansion(self):
        if len(self.json) > 0:
            set = self.json['set']
        else:
            name = 'Weaponized Piñata' if self.name == 'Weaponized PiÃ±ata' else self.name.rstrip()
            set = minions_by_name[name]['set']
        return set_names[CardSet[set]]


@dataclass
class List:
    id: int
    minions: {}

    def add_minion(self, minion: Minion):
        if minion.id not in self.minions:
            self.minions[minion.id] = minion


def read_log_file(filename: str):
    list_num = 0
    list_offset = 0
    minions = {}
    with open(filename) as file:
        for line_n in file:
            line = line_n[:-1]
            type, message = extract_message(line)
            if type == 'list-start':
                if message >= list_num:
                    list_num = message
                else:
                    list_offset = list_offset + 100000
                    list_num = message
            if type == 'list-item':
                parse_minion(message, minions, list_offset)
    return minions


WIN_LOG_PATH = 'C:\\Program Files (x86)\\Hearthstone\\Logs\\'
MAC_LOG_PATH = '/Applications/Hearthstone/Logs/'

if __name__ == '__main__':
    base_path = WIN_LOG_PATH if platform.system() == 'Windows' else MAC_LOG_PATH
    for log_folder in os.listdir(base_path):
        log_path = os.path.join(base_path, log_folder, 'Zone.log')
        minions = read_log_file(log_path)
        current_list = -1
        with open(log_folder + '.txt', 'w') as result:
            for list_id, minions_group in groupby(minions.values(), lambda minion: minion.list_id):
                minions_list_all = [minion for minion in list(minions_group)]
                minions_list = [minion for minion in minions_list_all if not minion.child_card]
                if len(minions_list) == 34:
                    minions_list.sort(key=lambda minion: minion.id)
                    if list_id != current_list:
                        result.write(f"T:{list_id} {len(minions_list)}\n")
                        current_list = list_id
                    for minion in minions_list:
                        result.write(f"{minion}\n")
                else:
                    if list_id != current_list:
                        print(f"T:{list_id} {len(minions_list_all)}\n")
                        current_list = list_id
                    for minion in minions_list_all:
                        print(minion.id, minion, minion.tags, minion.lists)
