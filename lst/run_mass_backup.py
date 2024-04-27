import os

from lst.backup_game import save_run
from parse_lst import read_all_games

if __name__ == '__main__':
    path = "G:\\.shortcut-targets-by-id\\1CFpsGpqz65IlXdBeou1MB5lTdJbYxjv1\\Long Strange Trip runs\\Leftmost Attack Runs"
    runs = read_all_games(
        path,
        [],
    )
    if not os.path.exists(path + "\\backup"):
        os.mkdir(path + "\\backup")
    for run in runs.runs:
        backup_name = run.log_name
        save_path = path + "\\" + "backup\\" + backup_name.replace(".log", "") + ".bkp"
        save_run(save_path, run)