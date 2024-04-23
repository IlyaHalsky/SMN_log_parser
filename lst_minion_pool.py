from collections import defaultdict

from minions_utils import minions_by_id

if __name__ == '__main__':
    pool = set()
    with open('csv_dump/appeared_times_1to1.txt', 'r') as f:
        for line in f:
            pool.add(line.split(',')[0])
    set_counts = defaultdict(int)
    rarity_counts = defaultdict(int)
    type_counts = defaultdict(int)
    has_type_count = defaultdict(int)
    class_counts = defaultdict(int)
    for id in pool:
        if id == 'SCH_199t':
            card_id = 'SCH_199'
        else:
            card_id = id
        minion = minions_by_id[card_id]
        set_counts[minion['set']] += 1
        rarity_counts[minion['rarity']] += 1
        races = minion.get('races', [])
        for race in races:
            type_counts[race] += 1
        if len(races) > 0:
            has_type_count['y'] += 1
        else:
            has_type_count['n'] += 1
        class_counts[minion['cardClass']] += 1
    set_counts = dict(sorted(set_counts.items(), key=lambda item: item[0]))
    rarity_counts = dict(sorted(rarity_counts.items(), key=lambda item: item[0]))
    type_counts = dict(sorted(type_counts.items(), key=lambda item: item[0]))
    class_counts = dict(sorted(class_counts.items(), key=lambda item: item[0]))
    print('set_counts', set_counts)
    print('rarity_counts', rarity_counts)
    print('type_counts', type_counts)
    print('has_type_count', has_type_count)
    print('class_counts', class_counts)
