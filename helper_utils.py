import os
import platform
import time
from typing import Iterator

import psutil

from download_card_defs import download_collectable


def hs_running():
    for pid in psutil.pids():
        if psutil.pid_exists(pid):
            try:
                if 'Hearthstone' in psutil.Process(pid).name():
                    return True
            except:
                pass
    return False


if platform.system() == 'Windows':
    clear_console = lambda: os.system('cls')
else:
    clear_console = lambda: os.system('clear')


def follow_file(file, sleep_sec=0.1) -> Iterator[str]:
    line = ''
    while True:
        tmp = file.readline()
        if tmp is not None and tmp != "":
            line += tmp
            if line.endswith("\n"):
                yield line
                line = ''
        elif hs_running():
            time.sleep(sleep_sec)
        else:
            break
    yield ''

def download_card_data():
    if not os.path.exists("./helper_data"):
        os.mkdir("./helper_data")
    if not os.path.exists("./helper_data/cards.collectible.json"):
        download_collectable("./helper_data")
