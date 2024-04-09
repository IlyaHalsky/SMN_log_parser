import random
from collections import defaultdict

if __name__ == '__main__':

    dups = 0
    for i in range(27478):
        counts = defaultdict(int)
        for card in random.choices(range(39), k=14):
            counts[card] += 1
        has_dup = 0
        for k, v in counts.items():
            if v > 1:
                has_dup = 1
        dups += has_dup
    print(dups, 27478)
    #cards = dict(sorted(counts.items(), key=lambda item: item[1]), reversed=True)
    #with open('cards2.txt', 'w') as w:
    #    for k, v in cards.items():
    #        w.write(f"{k}, {v}\n")
