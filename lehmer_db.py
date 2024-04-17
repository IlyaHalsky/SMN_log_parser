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
