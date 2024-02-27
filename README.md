## Say My Name log parser for Hearthstone

# Repo contains Say My Name Helper and ~~Say My Name Data Collector~~

# Before use:
0) Preferably: Remove previous logs from log directory
1) If you are using HDT, skip this step. Enable logs ([How To](https://github.com/HearthSim/Hearthstone-Deck-Tracker/wiki/Setting-up-the-log.config)) use this config [log.config](https://gist.github.com/IlyaHalsky/024db2ec71a4eabb660adb0cffcf5cb3)

# Say My Name helper
0) Download `smn_helper.exe` from [here](https://github.com/IlyaHalsky/SMN_log_parser/releases/latest)
1) Run `smn_helper.exe`
2) Terminal window will open, make it full screen
3) Enter Say My Name puzzle ([How To](https://docs.google.com/document/d/13LdaSziJMj0XjqXGdlMQIu1YyVA4qTMab1ODRsh5bqk/edit#heading=h.fzpuwdlu8y0t))
4) In terminal will be displayed answers to current board



# ------------------------------------- OLDER STUFF ---------------------------------------------
# ~~Say My Name Data Collector~~ _no longer needed_
# Before use:
0) Preferably: Remove previous logs from log directory
1) If you are using HDT, skip this step. Enable logs ([How To](https://github.com/HearthSim/Hearthstone-Deck-Tracker/wiki/Setting-up-the-log.config)) use this config [log.config](https://gist.github.com/IlyaHalsky/024db2ec71a4eabb660adb0cffcf5cb3)
1) Open Hearthstone (this will reset logs)
2) Enter Say My Name puzzle ([How To](https://docs.google.com/document/d/13LdaSziJMj0XjqXGdlMQIu1YyVA4qTMab1ODRsh5bqk/edit#heading=h.fzpuwdlu8y0t))
3) Press end turn several times (max. 45)
4) Exit Puzzle
5) Repeat 3-5 as many times as you want (if you are on Windows, on Mac logs will be truncated) 
6) Exit Hearthstone

# How to run:
Download latest release from [here](https://github.com/IlyaHalsky/SMN_log_parser/releases/tag/1.0)
or Clone repo and run `list_compiler.py`, requires python 3.8+

Program will output to local folder 3 files:
- `board_set.txt` - minions seen on board
- `correct_set.txt` - minions seen as a correct option
- `incorrect_set.txt` - minions seen as an incorrect option

You can enter these sets here:
[Say My Name catalog](https://docs.google.com/spreadsheets/d/19usNxtQtgAw4SjtZjCAKak6sZyHHuh7_1CWjcZ9G3VU/edit#gid=0)
