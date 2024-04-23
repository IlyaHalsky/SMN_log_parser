from collections import defaultdict

from minions_utils import minions_by_id

if __name__ == '__main__':
    had = set()
    with open('csv_dump/appeared_times_1to1.txt', 'r') as f:
        for line in f:
            minion = line.split(',', 1)[0].replace('SCH_199t', 'SCH_199')
            name = minions_by_id[minion]['name']
            had.add(name)
    for minion in minions_by_id.values():
        if minion['name'] not in had:
            print(minion['name'], minion)