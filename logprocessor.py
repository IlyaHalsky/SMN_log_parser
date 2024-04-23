import json

def load_json_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

attacker = ""

def format_minions(minions):

    output_lines = []
    group = []
    group1 = []
    for minion in minions:
        if 'PARENT_CARD' in minion:
            continue  # Skip minions with a parent card reference

        minion_id = minion['id']
        entity_name = minion['entityName']
        base_attack = int(minion.get('base_attack', 0))
        current_attack = int(minion.get('ATK', base_attack))
        health = int(minion.get('base_health', 0))
        attack_diff = current_attack - base_attack
        global attacker

        if 'attacking_id' in minion:
            attacker = f"{entity_name} attacks {minion['attacking_id']}"

        formatted_minion = f"{minion_id}: {entity_name}, {base_attack}+{attack_diff}, {health}"
        formatted_minion1 = f"{attack_diff}"
        group.append(formatted_minion)
        group1.append(formatted_minion1)

        if len(group) == 7:
            if (attacker != ""):
                output_lines.append(" || ".join(group))
                output_lines.append(attacker)
                attacker = ""
                group=[]
                print(group1)
                group1=[]
                output_lines.append(" || ".join(group))

                continue
            output_lines.append(" || ".join(group))
            group = []
    if group:
        output_lines.append(" || ".join(group) )

    return output_lines

file_path = "output_file.json"
minions_data = load_json_data(file_path)
formatted_output = format_minions(minions_data)

for line in formatted_output:
    print(line)
