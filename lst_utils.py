from collections import defaultdict

def rotate(l, n):
    return l[n:] + l[:n]


def check_for_cycles(boards):
    seen = defaultdict(list)
    for board in boards:
        for i in range(len(board) - 1):
            seen[','.join(map(str, rotate(board, i)))].append(board)

    for key, value in seen.items():
        if len(value) > 1:
            print(key, value)
