import json

from helper_utils import download_card_data

minions_by_id = {}
minions_by_name = {}
minions_by_dbfId = {}

def init_minions():
    global minions_by_id, minions_by_name, minions_by_dbfId
    download_card_data()
    minions_json = json.load(open('./helper_data/cards.collectible.json', encoding='utf-8'))
    minions_by_id = {card['id']: card for card in minions_json if card['type'] == 'MINION'}
    minions_by_name = {card['name']: card for card in minions_json if card['type'] == 'MINION'}
    minions_by_dbfId = {str(card['dbfId']): card for card in minions_json if card['type'] == 'MINION'}

init_minions()
