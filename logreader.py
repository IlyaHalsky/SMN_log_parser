import re
import json
def load_card_details(cards_json_path):
    try:
        with open(cards_json_path, 'r', encoding='utf-8') as file:
            cards_data = json.load(file)
    except UnicodeDecodeError:
        with open(cards_json_path, 'r', encoding='cp1252') as file:
            cards_data = json.load(file)
    card_details = {card['id']: card for card in cards_data}
    return card_details
def is_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def extract_log_data(zone_log_path, power_log_path):
    cards_dict = {}

    card_info_regex = re.compile(r'entity=\[id=(\d+) cardId=(\w+) name=([^]]+)\]')
    tag_value_regex = re.compile(r'tag=(\w+) value=(\d+)')
    attack_regex = re.compile(r'tag=LAST_AFFECTED_BY value=(\d+)')

    with open(zone_log_path, 'r') as file:
        for line in file:
            card_match = card_info_regex.search(line)
            if card_match:
                card_id, cardId, entityName = card_match.groups()
                if entityName == "???" or cardId.startswith("TB_"):
                    continue
                if card_id not in cards_dict:
                    cards_dict[card_id] = {
                        "id": card_id,
                        "cardId": cardId,
                        "entityName": entityName,
                        "base_attack": card_details[cardId].get('attack'),
                        "base_health": card_details[cardId].get('health'),
                        "cardClass": card_details[cardId].get('cardClass'),
                        "rarity": card_details[cardId].get('rarity'),
                    }

                attrs = tag_value_regex.findall(line)
                for tag, value in attrs:
                    cards_dict[card_id][tag] = int(value)

    with open(power_log_path, 'r') as file:
        current_id = None
        for line in file:
            entity_id_match = re.search(r'Creating ID=(\d+) CardID=\w+', line)
            if entity_id_match:
                current_id = entity_id_match.group(1)

            if current_id and 'tag=LAST_AFFECTED_BY value=' in line:
                attacked_by_id = re.search(r'tag=LAST_AFFECTED_BY value=(\d+)', line).group(1)
                if current_id in cards_dict:
                    cards_dict[current_id]['attacking_id'] = int(attacked_by_id)
                if attacked_by_id in cards_dict:
                    cards_dict[attacked_by_id]['attacker_id'] = int(current_id)

            if current_id and 'tag=ATK value=' in line:
                attack_value = re.search(r'tag=ATK value=(\d+)', line).group(1)
                cards_dict[current_id]['ATK'] = int(attack_value)

    return list(cards_dict.values())

def save_to_json(data, output_file_path):
    with open(output_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

cards_json_path = "cards.json"
zone_log_path = "Zone.log"
power_log_path = "Power.log"
output_file_path = "output_file.json"
card_details = load_card_details(cards_json_path)
zone_log_path = "C:\Program Files (x86)\Hearthstone\Logs\Hearthstone_2024_04_22_21_42_14\Zone.log"
power_log_path = "C:\Program Files (x86)\Hearthstone\Logs\Hearthstone_2024_04_22_21_59_24\Power.log"
output_file_path = "output_file.json"

card_data = extract_log_data(zone_log_path, power_log_path)
save_to_json(card_data, output_file_path)
print("Data extracted and updated with attack relationships, saved to JSON.")
