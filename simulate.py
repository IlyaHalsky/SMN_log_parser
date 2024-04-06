import random
from collections import defaultdict

from tqdm import tqdm

if __name__ == '__main__':
    count = defaultdict(int)
    sims = 10000000
    for i in tqdm(range(1, sims)):
        board = []
        while len(board) < 14:
            minion = random.randint(0, 3000)
            if minion not in board:
                board.append(minion)
        wrong = []
        for i in range(6):
            wrong.append(random.randint(0, 3000))
        dups = 0
        for w in wrong:
            if w in board:
                dups += 1
        count[dups] += 1
    for k, v in count.items():
        print(k, v/sims)