import json
import os
import platform
from configparser import ConfigParser
from dataclasses import dataclass

def parse_separator(separator):
    if separator == 'SPACE':
        return ' '
    if separator == 'TAB':
        return '\t'
    return separator

@dataclass
class LSTConfig:
    config: ConfigParser

    def __post_init__(self):
        self.hs_logs_path = self.config['hs']['logs_path']

        self.show_attack_add = int(self.config['display']['attack_add']) == 1
        self.show_attack_full = int(self.config['display']['attack_full']) == 1
        self.show_attack_base = int(self.config['display']['attack_base']) == 1
        self.show_health = int(self.config['display']['health']) == 1
        self.show_mana = int(self.config['display']['mana']) == 1
        self.show_minion_name = int(self.config['display']['minion_name']) == 1
        self.show_set = int(self.config['display']['set']) == 1

        self.log_array_separator = parse_separator(self.config['logging']['array_separator'])
        self.log_type_seperator = parse_separator(self.config['logging']['type_separator'])
        self.log_attack_add = int(self.config['logging']['attack_add']) == 1
        self.log_attack_full = int(self.config['logging']['attack_full']) == 1
        self.log_attack_base = int(self.config['logging']['attack_base']) == 1
        self.log_health = int(self.config['logging']['health']) == 1
        self.log_mana = int(self.config['logging']['mana']) == 1
        self.log_minion_id = int(self.config['logging']['minion_id']) == 1
        self.log_set = int(self.config['logging']['set']) == 1

    def to_print(self):
        return json.dumps(
            {s: dict(self.config.items(s)) for s in self.config.sections()},
            indent=2
        )


def generate_default_config():
    config = ConfigParser()
    config['hs'] = {
        'logs_path': 'C:\\Program Files (x86)\\Hearthstone\\Logs\\' if platform.system() == 'Windows' else '/Applications/Hearthstone/Logs/'
    }
    config['display'] = {
        'attack_add': '1',
        'attack_full': '0',
        'attack_base': '0',
        'health': '0',
        'mana': '0',
        'minion_name': '0',
        'set': '0',
    }

    config['logging'] = {
        'array_separator': ',',
        'type_separator': ';',
        'attack_add': '1',
        'attack_full': '0',
        'attack_base': '0',
        'health': '0',
        'mana': '0',
        'minion_id': '0',
        'set': '0',
    }

    # config['highlight'] = {
    #    'wip': 'wip',
    # }
    #
    # config['privacy'] = {
    #    'share_data': '0',
    #    'username': 'private',
    # }
    return config


LST_CONFIG_PATH = './helper_data/lst_helper_config.txt'


def init_config():
    with open(LST_CONFIG_PATH, 'w') as file:
        generate_default_config().write(file)

def merge_configs():
    config = ConfigParser()
    config.read(LST_CONFIG_PATH)
    default = generate_default_config()
    for section in default.sections():
        if config.has_section(section):
            for option in default.options(section):
                if not config.has_option(section, option):
                    config.set(section, option, default[section][option])
        else:
            config.add_section(section)
            for key, value in default.items(section):
                config.set(section, key, value)
    with open(LST_CONFIG_PATH, 'w') as file:
        config.write(file)


def read_config():
    if not os.path.exists(LST_CONFIG_PATH):
        init_config()
    else:
        merge_configs()
    config = ConfigParser()
    config.read(LST_CONFIG_PATH)
    return LSTConfig(config)


if __name__ == '__main__':
    # init_config()
    config = read_config()
    print(config.log_attack_add)
