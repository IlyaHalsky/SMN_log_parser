from collections import defaultdict

from minions_utils import minions_by_id

if __name__ == '__main__':
    rarities = defaultdict(int)
    with open('csv_dump/appeared_times_1to1.txt', 'r') as f:
        for line in f:
            minion = line.split(',', 1)[0].replace('SCH_199t', 'SCH_199')
            count = line.split(',', 1)[1][1:-1]
            json = minions_by_id[minion]
            rarity = minions_by_id[minion]['rarity']
            rarities[rarity] += 1
            list = [minion, count, json['name'], json['rarity'], json['cost'], json['attack'], json['health']]
            print(";".join(map(str, list)))
    print(rarities)