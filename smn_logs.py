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


def parse_minion(log, minions):
    change_list_match = re.match(
        r'changeList: id=(\d+)', log
    )
    match = re.search(r'\[id=(\d+) cardId=.*? name=(.*?)\]', log)
    if match:
        id = int(match.group(1))
        name = match.group(2)
        if id not in minions:
            minions[id] = Minion(int(change_list_match.group(1)), id, name, [])
        elif minions[id].name == '???':
            minions[id].name = name
        tags = re.search(r'\[type=TAG_CHANGE.*tag=(.*?) value=(.*?)\]', log)
        if tags:
            minions[id].tags.append((tags.group(1),tags.group(2)))
    return None


@dataclass
class Minion:
    list_id: int
    id: int
    name: str
    tags: []
    spell: bool = False

    def __post_init__(self):
        self.spell = self.name == '???'

    def __repr__(self):
        player = 'O' if ('CONTROLLER', '2 ') in self.tags else 'P'
        position = next((tag[1] for tag in self.tags if tag[0] == 'ZONE_POSITION'), '')
        tpe = 'S' if self.spell else 'M'
        return f'{tpe}|{self.name}|{player}:{position}'


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
        log_path = os.path.join(base_path, log_folder, 'Zone.log')
        minions = {}
        with open(log_path) as file:
            for line_n in file:
                line = line_n[:-1]
                type, message = extract_message(line)
                if type == 'list-item':
                    parse_minion(message, minions)
        current_list = -1
        with open(log_folder+'.txt', 'w') as result:
            for list_id, minions_group in groupby(minions.values(), lambda minion: minion.list_id):
                minions_list = list(minions_group)
                minions_list.sort(key=lambda minion: minion.id)
                if list_id != current_list:
                    print(f"T:{list_id} {len(minions_list)}")
                    result.write(f"T:{list_id} {len(minions_list)}\n")
                    current_list = list_id
                for minion in minions_list:
                    print(minion)
                    result.write(f"{minion}\n")

