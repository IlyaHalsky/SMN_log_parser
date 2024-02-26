## Say My Name log parser for Hearthstone

# Before use:
1) Enable logs ([How To](https://github.com/HearthSim/Hearthstone-Deck-Tracker/wiki/Setting-up-the-log.config))
2) Open Hearthstone (this will reset logs)
3) Enter Say My Name puzzle ([How To](https://docs.google.com/document/d/13LdaSziJMj0XjqXGdlMQIu1YyVA4qTMab1ODRsh5bqk/edit#heading=h.fzpuwdlu8y0t))
4) Press end turn several times (max. 45)
5) Exit Puzzle
6) Repeat 3-5 as many times as you want (if you are on Windows, on Mac logs will be truncated) 
7) Exit Hearthstone

# How to run:
- Easy: Download latest release from [here](https://github.com/IlyaHalsky/SMN_log_parser/releases/tag/1.0)
- Hard: Clone repo and run `list_compiler.py`, requires python 3.8+

Program will output to local folder 3 files:
- `board_set.txt` - minions seen on board
- `correct_set.txt` - minions seen as a correct option
- `incorrect_set.txt` - minions seen as an incorrect option

You can enter these sets here:
[Say My Name catalog](https://docs.google.com/spreadsheets/d/19usNxtQtgAw4SjtZjCAKak6sZyHHuh7_1CWjcZ9G3VU/edit#gid=0)
