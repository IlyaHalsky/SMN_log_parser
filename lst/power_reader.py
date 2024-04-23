import re
from dataclasses import dataclass

from tqdm import tqdm


@dataclass
class PowerEntity:
    entity_id: int
    card_id: str
    tags: []

    def get_tag(self, name: str):
        return next((tag[1] for tag in self.tags if tag[0] == name), None)

    @property
    def player(self):
        if (controller := self.get_tag('CONTROLLER')) is None:
            return 0
        else:
            return int(controller) % 2

    @property
    def affected_by(self):
        if (last_affected_by := self.get_tag('LAST_AFFECTED_BY')) is None:
            return None
        else:
            return int(last_affected_by)

    @property
    def current_attack(self):
        if (attack := self.get_tag('ATK')) is not None:
            return int(attack)
        else:
            return None

    @property
    def health(self):
        if (health := self.get_tag('HEALTH')) is not None:
            return int(health)
        else:
            return None

    @property
    def damage(self):
        if (damage := self.get_tag('DAMAGE')) is not None:
            return int(damage)
        else:
            return None


FULL_ENTITY_REGEX = re.compile("^[DWE] [\d:.]+ .+ - FULL_ENTITY - Creating ID=(\d+) CardID=(\w*)$")
TAG_REGEX = re.compile("^[DWE] [\d:.]+ .+ -     tag=(\w*) value=(\w*)$")


def read_power_entities(filename):
    entities = {}
    current_entity_id = None
    with open(filename, 'r') as f:
        for line in tqdm(f, desc="Reading power entities"):
            line = line.strip()
            entity = FULL_ENTITY_REGEX.match(line)
            if entity:
                new_entity = PowerEntity(int(entity.group(1)), entity.group(2), [])
                current_entity_id = new_entity.entity_id
                entities[current_entity_id] = new_entity
            if current_entity_id is not None:
                tag = TAG_REGEX.match(line)
                if tag:
                    entities[current_entity_id].tags.append((tag.group(1), tag.group(2)))
    return entities
