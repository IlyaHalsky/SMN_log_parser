from lst_utils import check_for_cycles
from parse_lst import read_all_games

def decode_board(swaps, board):
    board = board.copy()
    for a, b in swaps:
        a_i, b_i = board.index(a), board.index(b)
        board[a_i], board[b_i] = board[b_i], board[a_i]
    return board

if __name__ == '__main__':
    runs = read_all_games(
        "G:\\.shortcut-targets-by-id\\1CFpsGpqz65IlXdBeou1MB5lTdJbYxjv1\\Long Strange Trip runs\\Leftmost Attack Runs"
    )
    print(f"Total turns: {len(runs.all_games)}")
    for run in runs.runs:
        decoded_boards = []
        swaps = []
        for game in run.games:
            board = game.attack_add.copy()
            #board[0], board[7] = board[7], board[0]
            decoded = decode_board(swaps, board)
            swaps.append((board[0], board[7]))
            decoded_boards.append(decoded)
        check_for_cycles(decoded_boards)
        break
