import json
import os

from helper_utils import download_card_data

minions_by_id = {}
cards_by_id = {}
minions_by_name = {}
cards_by_dbfId = {}

def init_minions():
    global minions_by_id, cards_by_id, minions_by_name, cards_by_dbfId
    download_card_data()
    cards_path = os.environ.get('CARDS_PATH', './helper_data/cards.collectible.json')
    minions_json = json.load(open(cards_path, encoding='utf-8'))
    minions_by_id = {card['id']: card for card in minions_json if card['type'] == 'MINION'}
    cards_by_id = {card['id']: card for card in minions_json}
    minions_by_name = {card['name']: card for card in minions_json if card['type'] == 'MINION'}
    cards_by_dbfId = {str(card['dbfId']): card for card in minions_json}

init_minions()
