import random
from collections import defaultdict
import matplotlib.pylab as plt


import numpy as np
from numpy import nonzero
from tqdm import tqdm

if __name__ == '__main__':
    count = defaultdict(int)
    success_odss = 0.0004
    simulations = 1000000
    max_runs = 300
    before_success = defaultdict(int)
    print(0, int(1 / success_odss))
    for i in tqdm(range(0, simulations)):
        array = np.random.randint(0, int(1 / success_odss), max_runs * 45)
        first = nonzero(array == 0)[0]
        if len(first) == 0:
            continue
        else:
            before_success[int(first[0])] += 1
    print(before_success)
    lists = sorted(before_success.items())  # sorted by key, return a list of tuples

    x, y = zip(*lists)  # unpack a list of pairs into two tuples
    x = np.array(x) / 45
    y = np.array(y)
    sum = 0
    for i in range(len(x)):
        print(sum)
        y[i] += sum
        sum = y[i]
    y= np.array(y) / simulations * 100


    plt.xlim(0, max_runs)
    plt.ylim(0, 100)
    plt.plot(x, y)
    plt.show()