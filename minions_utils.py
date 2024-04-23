import json
import os
import sys
from collections import defaultdict


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


minions_json = json.load(open(resource_path('cards.collectible.json'), encoding="utf8"))
minions_by_id = {card['id']: card for card in minions_json if card['type'] == 'MINION'}
minions_by_name = {card['name']: card for card in minions_json if card['type'] == 'MINION'}
minions_by_dbfId = {str(card['dbfId']): card for card in minions_json if card['type'] == 'MINION'}

