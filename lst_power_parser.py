import logging
import os
import time
import traceback

from tqdm import tqdm

from helper_utils import hs_running
from lst.lst_config import read_config
from lst.power_reader import read_power_entities
from lst_helper import log_game
from parse_lst import read_all_games
from smn_logs import RESTART_OFFSET

if __name__ == '__main__':
    try:
        config = read_config()
        print(config.to_print())
        if hs_running():
            print('Waiting for Hearthstone to close, press "Leave" in puzzle and close Hearthstone')
            hs_closed = False
            while not hs_closed:
                if not hs_running():
                    hs_closed = True
                time.sleep(1)
        log_folders = [folder for folder in os.listdir(config.hs_logs_path) if 'Hearthstone_' in folder]
        log_folders.sort()
        current_log_folder = log_folders[-1]
        prev_log_folder = log_folders[-2]
        log_date = current_log_folder.replace('Hearthstone_', '')
        zone_path = os.path.join(config.hs_logs_path, prev_log_folder)
        power_path = os.path.join(config.hs_logs_path, current_log_folder, 'Power.log')
        print(f"Current zone log path: {power_path}")
        print(f"Current power log path: {zone_path}")
        logging.basicConfig(filename=f'lst_power_{log_date}.log', filemode='w', format='%(message)s')
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        run = read_all_games(zone_path, ['Zone.log'], use_backup=False).all_sessions[-1]
        games = run.last_offset_games
        power_entities = read_power_entities(power_path)
        for game in tqdm(games, desc='Combining logs'):
            game_offset = game.game_offset * RESTART_OFFSET
            for minion in game.minions:
                entity_id = minion.id % RESTART_OFFSET
                power_entity = power_entities[entity_id]
                if power_entity.card_id != '':
                    assert power_entity.card_id == minion.card_id, f"Card ID mismatch {power_entity.card_id} != {minion.card_id}, {minion}, {power_entity}"
                    if power_entity.affected_by is not None:
                        attacker = minion
                        defender = game.minion_by_id(power_entity.affected_by + game_offset)
                        assert power_entity.damage == defender.current_attack, "Damage mismatch"
                        game.attacker = attacker
                        game.defender = defender

        for game in tqdm(games, desc='Writing logs'):
            header = f"Turn: {game.list_id % RESTART_OFFSET - 2}"
            log_game(header, game, logger, config)
    except Exception as e:
        traceback.print_exc()
        with open("./lst_power_parser_crash.txt", "w") as crashLog:
            crashLog.write(traceback.format_exc())
