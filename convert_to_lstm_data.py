import numpy as np

from parse_lst import read_all_games

def board_to_oz(board):
    result = [[0]*14 for i in range(14)]
    for i, m in enumerate(board.attack_add):
        result[i][m - 1] = 1
    return result

if __name__ == '__main__':
    runs = read_all_games(
        "G:\\.shortcut-targets-by-id\\1CFpsGpqz65IlXdBeou1MB5lTdJbYxjv1\\Long Strange Trip runs\\Leftmost Attack Runs",
        []
    )
    for i, run in enumerate(runs.runs):
        arrays = []
        for game in run.games:
            arrays.append(np.array(board_to_oz(game)))
        arrays = np.array(arrays)
        print(arrays.shape)
        np.save(f"dataset/{i}.npy", arrays)
