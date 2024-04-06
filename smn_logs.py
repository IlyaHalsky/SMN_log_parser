import json
import platform
import re
import shutil
import sys
from dataclasses import dataclass
from itertools import groupby

import cv2
import numpy as np
import requests
from hearthstone.enums import CardSet

from card_sets import set_names

TIMESTAMP_RE = re.compile(r"^([DWE]) ([\d:.]+) (.+)$")
MESSAGE_RE = re.compile(r"^(.*) - (.*)$")
LIST_START = re.compile(r"ZoneMgr.AddServerZoneChanges\(\) - taskListId=(\d*) changeListId=(\d*)")
LIST_ITEM = re.compile(r"ZoneMgr.AddServerZoneChanges\(\) - AddChange\(\) (changeList.*)")
LIST_END = re.compile(r"ZoneChangeList.Finish\(\) - id=(\d*)")


def extract_message(log_line):
    if log_line is None or log_line == '':
        return None, None, None
    message = TIMESTAMP_RE.match(log_line).group(3)
    date = TIMESTAMP_RE.match(log_line).group(2)
    if message is None:
        return None, None
    if LIST_START.match(message):
        return date, "list-start", int(LIST_START.match(message).group(2))
    if LIST_ITEM.match(message):
        return date, "list-item", LIST_ITEM.match(message).group(1)
    if LIST_END.match(message):
        return date, "list-end", int(LIST_END.match(message).group(1))
    return None, None, None


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
minions_by_dbfId = {str(card['dbfId']): card for card in minions_json if card['type'] == 'MINION'}


def parse_minion(date, filename, log, minions, list_offset):
    change_list_match = re.match(
        r'changeList: id=(\d+)', log
    )
    list_id = int(change_list_match.group(1)) + list_offset
    match = re.search(r'\[id=(\d+) cardId=(.*?) name=(.*?)\]', log)
    if match:
        minion_id = int(match.group(1)) + list_offset
        card_id = match.group(2)
        name = match.group(3)
        name = 'Weaponized Piñata' if name == 'Weaponized PiÃ±ata' else name.rstrip()
        if minion_id not in minions:
            minions[minion_id] = Minion(
                log_name=filename,
                log_date=date,
                list_id=list_id,
                id=minion_id,
                card_id=card_id,
                name=name,
                tags=[],
                lists=[list_id],
            )
            minions[minion_id].json = minions_by_id.get(card_id, {})
        elif minions[minion_id].name == '???':
            minions[minion_id].name = name
            minions[minion_id].json = minions_by_name.get(name, {})
        tags = re.search(r'\[type=TAG_CHANGE.*tag=(.*?) value=(.*?)\]', log)
        if tags:
            minions[minion_id].tags.append((tags.group(1), tags.group(2)))
            minions[minion_id].lists.append(list_id)
            if tags.group(1) == 'OVERRIDECARDNAME':
                value = tags.group(2)[:-1]
                if value in minions_by_dbfId:
                    json = minions_by_dbfId[value]
                    minions[minion_id].card_id = json['id']
                    minions[minion_id].name = json['name']
                    minions[minion_id].json = json
        position = re.search(r'zone=HAND zonePos=(\d+) cardId=HM_101 player=1', log)
        if position:
            minions[minion_id].tags.append(('ZONE_POSITION', position.group(1)))
        hide = re.search(r'\[type=HIDE_ENTITY entity=\[id=', log)
        if hide:
            minions[minion_id].shown = False
        show = re.search(r'\[type=SHOW_ENTITY entity=\[id=', log)
        if show:
            minions[minion_id].shown = True
    return None


@dataclass
class Minion:
    log_name: str
    log_date: str
    list_id: int
    id: int
    card_id: str
    name: str
    tags: []
    lists: []
    spell: bool = False

    def __post_init__(self):
        self.spell = self.name == '???'
        self.json = {}
        self.shown = True
        self.color = [0,0,0]

    # def __repr__(self):
    #    player = 'O' if ('CONTROLLER', '2 ') in self.tags else 'P'
    #    position = next((tag[1] for tag in self.tags if tag[0] == 'ZONE_POSITION'), '')
    #    tpe = 'S' if self.spell else 'M'
    #    return f'{tpe}|{self.name}|{player}:{position}'

    @property
    def dbf_id(self):
        return self.json['dbfId']

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
    def position_safe(self):
        return int(next((tag[1] for tag in self.tags if tag[0] == 'ZONE_POSITION'), 0)) - 1

    @property
    def used(self):
        return any(map(lambda x: x == ("ZONE", "GRAVEYARD "), self.tags))

    @property
    def last_set_aside(self):
        return len(self.tags) != 0 and self.tags[-1] == ("ZONE", "SETASIDE ")

    @property
    def sort_key(self):
        return (self.player, self.position)

    @property
    def sort_key_safe(self):
        return (self.player, self.position_safe, self.name)

    @property
    def expansion(self):
        if len(self.json) > 0:
            set = self.json['set']
        else:
            set = minions_by_name[self.name]['set']
        return set_names[CardSet[set]]

    @property
    def en_image(self):
        url = f"https://art.hearthstonejson.com/v1/render/latest/enUS/256x/{self.card_id}.png"
        if not os.path.exists("./image_cache"):
            os.makedirs(f"./image_cache")
        if not os.path.exists(f"./image_cache/{self.card_id}.png"):
            response = requests.get(url, stream=True)
            with open(f"./image_cache/{self.card_id}.png", 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response
        image = cv2.imread(f"./image_cache/{self.card_id}.png", cv2.IMREAD_UNCHANGED)
        return image

    @property
    def mana(self):
        return self.json['cost']

    @property
    def attack(self):
        return self.json['attack']

    @property
    def health(self):
        return self.json['health']



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
            date, type, message = extract_message(line)
            if type == 'list-start':
                if message >= list_num:
                    list_num = message
                else:
                    list_offset = list_offset + 100000
                    list_num = message
            if type == 'list-item':
                parse_minion(date, filename, message, minions, list_offset)
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
