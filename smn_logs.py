import os
import platform
import re
from dataclasses import dataclass
from itertools import groupby

TIMESTAMP_RE = re.compile(r"^([DWE]) ([\d:.]+) (.+)$")
MESSAGE_RE = re.compile(r"^(.*) - (.*)$")
LIST_START = re.compile(r"ZoneMgr.AddServerZoneChanges\(\) - taskListId=(\d*) changeListId=(\d*)")
LIST_ITEM = re.compile(r"ZoneMgr.AddServerZoneChanges\(\) - AddChange\(\) (changeList.*)")
LIST_END = re.compile(r"ZoneChangeList.Finish\(\) - id=(\d*)")


def extract_message(log_line):
    message = TIMESTAMP_RE.match(log_line).group(3)
    if LIST_START.match(message):
        return "list-start", int(LIST_START.match(message).group(2))
    if LIST_ITEM.match(message):
        return "list-item", LIST_ITEM.match(message).group(1)
    if LIST_END.match(message):
        return "list-end", int(LIST_END.match(message).group(1))
    return None, None


def parse_minion(log, minions, list_offset):
    change_list_match = re.match(
        r'changeList: id=(\d+)', log
    )
    list_id = int(change_list_match.group(1)) + list_offset
    match = re.search(r'\[id=(\d+) cardId=.*? name=(.*?)\]', log)
    if match:
        minion_id = int(match.group(1)) + list_offset
        name = match.group(2)
        if minion_id not in minions:
            minions[minion_id] = Minion(list_id, minion_id, name, [], [list_id])
        elif minions[minion_id].name == '???':
            minions[minion_id].name = name
        tags = re.search(r'\[type=TAG_CHANGE.*tag=(.*?) value=(.*?)\]', log)
        if tags:
            minions[minion_id].tags.append((tags.group(1),tags.group(2)))
            minions[minion_id].lists.append(list_id)
    return None


@dataclass
class Minion:
    list_id: int
    id: int
    name: str
    tags: []
    lists: []
    spell: bool = False

    def __post_init__(self):
        self.spell = self.name == '???'

    def __repr__(self):
        player = 'O' if ('CONTROLLER', '2 ') in self.tags else 'P'
        position = next((tag[1] for tag in self.tags if tag[0] == 'ZONE_POSITION'), '')
        tpe = 'S' if self.spell else 'M'
        return f'{tpe}|{self.name}|{player}:{position}'

    @property
    def child_card(self):
        return any(tag[0] == 'PARENT_CARD' for tag in self.tags)

@dataclass
class List:
    id: int
    minions: {}

    def add_minion(self, minion: Minion):
        if minion.id not in self.minions:
            self.minions[minion.id] = minion

WIN_LOG_PATH = 'C:\\Program Files (x86)\\Hearthstone\\Logs\\'
MAC_LOG_PATH = '/Applications/Hearthstone/Logs/'

if __name__ == '__main__':
    base_path = WIN_LOG_PATH if platform.system() == 'Windows' else MAC_LOG_PATH
    for log_folder in os.listdir(base_path):
        list_num = 0
        list_offset = 0
        log_path = os.path.join(base_path, log_folder, 'Zone.log')
        minions = {}
        with open(log_path) as file:
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
        current_list = -1
        with open(log_folder+'.txt', 'w') as result:
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

