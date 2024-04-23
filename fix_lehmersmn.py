if __name__ == '__main__':
    lines = open('analysis/lehmer_smn.txt').readlines()
    with open('analysis/lehmer_smn.txt', 'w') as f:
        seen = set()
        for line in lines:
            if line not in seen:
                f.write(line)
                seen.add(line)