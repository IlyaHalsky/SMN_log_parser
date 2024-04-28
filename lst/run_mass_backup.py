import os

from parse_lst import read_all_games

if __name__ == '__main__':
    path = "G:\\.shortcut-targets-by-id\\1CFpsGpqz65IlXdBeou1MB5lTdJbYxjv1\\Long Strange Trip runs\\Leftmost Attack Runs"
    runs = read_all_games(
        path,
        [
            "zulukiwi11.log",
        ],
    )
