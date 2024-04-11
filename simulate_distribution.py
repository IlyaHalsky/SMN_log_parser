import random
from collections import defaultdict

if __name__ == '__main__':
    counts = defaultdict(int)
    for i in range(35537):
        for card in random.sample(range(3041), 14):
            counts[card] += 1
    cards = dict(sorted(counts.items(), key=lambda item: item[1]), reversed=True)
    with open('cards2.txt', 'w') as w:
        for k, v in cards.items():
            w.write(f"{k}, {v}\n")
