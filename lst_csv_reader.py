import json
from collections import defaultdict

from tqdm import tqdm

if __name__ == '__main__':
    seen = set()
    numbers = defaultdict(int)
    cards = defaultdict(int)
    has_dup = 0
    total = 0
    sets_all = set()
    counts = defaultdict(lambda: defaultdict(int))
    with open('dump.txt', 'w') as w:
        with open('mysterious.csv',  encoding="utf8") as csvfile:
            for line in tqdm(csvfile.readlines()):
                line = line[:-2]
                json_raw = '{' + line.split("{", 1)[1]
                if json_raw in seen:
                    continue
                else:
                    seen.add(json_raw)
                    parsed = json.loads(json_raw)
                    attack_add = list(map(lambda v: v['AtkAdd'], parsed.values()))
                    if len(attack_add) < 14 or any([a == 0 for a in attack_add]):
                        continue
                    numbers[','.join(map(str, attack_add[0:7]))] += 1
                    numbers[','.join(map(str, attack_add[7:14]))] += 1
                    result = ''
                    sets = defaultdict(int)
                    for k, v in parsed.items():
                        counts[v['CardID']][v['AtkAdd']]+=1
                        if v['ControllerSide'] == 2:
                            sets[v['Set']] += 1

                        sets_all.add(v['Set'])
                        cards[v['CardID']] += 1
                        result += ' ' + str(v['AtkAdd'])
                    setss  = ''
                    for k, v in sets.items():
                        if v > 1:
                            setss += f' {k}: {v} '
                    if len(setss) > 0:
                        has_dup += 1
                    total += 1
                    w.write(setss + result + '\n')
    for k, v in numbers.items():
        if v > 1:
            print(k, v)
    cards = dict(sorted(cards.items(), key=lambda item: item[1]), reversed=True)
    with open('cards.txt', 'w') as w:
        for k, v in cards.items():
            w.write(f"{k}, {v}\n")
    print(has_dup, total)
    print(len(sets_all))
    counts = dict(sorted(counts.items(), key=lambda item: item[0]))
    with open('counts.txt', 'w') as w:
        for k, v in counts.items():
            v = dict(sorted(v.items(), key=lambda item: item[0]))
            w.write(f'{k}, {v}\n')


