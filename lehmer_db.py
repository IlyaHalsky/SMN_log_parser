import random
from collections import defaultdict
import matplotlib.pyplot as plt


class LehmerDB:
    def __init__(self, file_name):
        self.codes = set()
        self.lehmers = []
        with open(file_name, "r") as f:
            for line in f.readlines():
                line = line.strip()
                if len(line) > 0:
                    [code, attack, minions] = line.split(";")
                    self.codes.add(int(code))
                    self.lehmers.append((int(code), attack, minions))

    def seen(self, code):
        if code in self.codes:
            return list(filter(lambda x: x[0] == code, self.lehmers))
        else:
            return None


lehmer_db_csv = LehmerDB("csv_dump/lehmer.txt")
lehmer_db_smn = LehmerDB("analysis/lehmer_smn.txt")
lehmer_db_lst = LehmerDB("analysis/lehmer.txt")

if __name__ == '__main__':
    buckets = defaultdict(int)
    bucket_size = 87178291199 / 1000
    for code in lehmer_db_csv.codes:
        buckets[int(code / bucket_size)] += 1
    for code in lehmer_db_lst.codes:
        buckets[int(code / bucket_size)] += 1
    buckets = dict(sorted(buckets.items(), key=lambda item: item[0]))
    plt.figure(figsize=(50, 20))
    plt.bar(list(buckets.keys()), buckets.values(), color='g')
    plt.show()
    print(len(lehmer_db_csv.codes) + len(lehmer_db_lst.codes))
    for k, v in buckets.items():
        print(k, v)

    all_codes = []
    for code in lehmer_db_csv.codes:
        all_codes.append(code)
    for code in lehmer_db_lst.codes:
        all_codes.append(code)
    all_codes.sort()

    buckets2 = defaultdict(int)
    for i in range(len(all_codes)):
        buckets2[int(random.randint(0, 87178291199)/ bucket_size) ] += 1
    buckets2 = dict(sorted(buckets2.items(), key=lambda item: item[0]))
    plt.figure(figsize=(50, 20))
    plt.bar(list(buckets2.keys()), buckets2.values(), color='r')
    plt.show()

    with open("lehmer.txt", "w") as f:
        for code in all_codes:
            f.write(str(code) + "\n")