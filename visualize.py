import os
import shutil

import cv2
import numpy as np
import requests

from smn_game import Game


def count_size(images, scooch=1):
    total_width = 0
    max_height = 0
    for i, img in enumerate(images):
        height, width = img.shape[:2]
        if i + 1 != len(images):
            total_width += width // scooch
        else:
            total_width += width
        max_height = max(max_height, height)
    return total_width, max_height


def combine(image, card, base, offset_h, offset_w):
    h, w = image.shape[:2]
    if card.color == (0, 0, 0):
        blured_alpha = np.zeros(image.shape[:2])
    else:
        blured_alpha = cv2.GaussianBlur(image[:, :, 3], (15, 15), 0)
    border = np.where(blured_alpha > 0, np.ones(image.shape[:2]), np.zeros(image.shape[:2]))
    border = cv2.merge([border * card.color[0], border * card.color[1], border * card.color[2], border * 255])
    border_alpha = cv2.merge([border[:, :, 3], border[:, :, 3], border[:, :, 3], border[:, :, 3]])
    combined = np.where(border_alpha > 0, border, base[offset_h: offset_h + h, offset_w: offset_w + w, :])
    alpha = cv2.merge([image[:, :, 3], image[:, :, 3], image[:, :, 3], image[:, :, 3]])
    combined = np.where(alpha != 255, combined, image)
    base[offset_h: offset_h + h, offset_w:offset_w + w] = combined

def en_image(minion):
   url = f"https://art.hearthstonejson.com/v1/render/latest/enUS/256x/{minion.card_id}.png"
   if not os.path.exists("./image_cache"):
       os.makedirs(f"./image_cache")
   if not os.path.exists(f"./image_cache/{minion.card_id}.png"):
       response = requests.get(url, stream=True)
       with open(f"./image_cache/{minion.card_id}.png", 'wb') as out_file:
           shutil.copyfileobj(response.raw, out_file)
       del response
   image = cv2.imread(f"./image_cache/{minion.card_id}.png", cv2.IMREAD_UNCHANGED)
   return image

def create_board_image(game: Game, bg=0):
    opponent_images = [en_image(minion) for minion in game.opponents_board]
    player_images = [en_image(minion) for minion in game.players_board]
    spells = [en_image(minion) for minion in game.spells]
    max_width = 0
    total_height = 0
    w_o, h_o = count_size(opponent_images)
    max_width = max(max_width, w_o)
    total_height += h_o
    w_p, h_p = count_size(player_images)
    max_width = max(max_width, w_p)
    total_height += h_p
    scooch = 2
    w, h_l = count_size(spells, scooch)
    max_width = max(max_width, w)
    total_height += h_l
    result = np.ones((total_height, max_width, 4), dtype=np.uint8) * bg
    offset_w = 0
    offset_h = 0
    opponent_offset = (max_width - w_o) // 6
    for opponent, opp in zip(opponent_images, game.opponents_board):
        h, w = opponent.shape[:2]
        combine(opponent, opp, result, offset_h, offset_w)
        offset_w += w + opponent_offset
    offset_w = 0
    offset_h += h_o
    player_offset = (max_width - w_p) // 6
    for player, pl in zip(player_images, game.players_board):
        h, w = player.shape[:2]
        combine(player, pl, result, offset_h, offset_w)
        offset_w += w + player_offset
    offset_w = 0
    offset_h += h_p
    for leftout, spell in zip(spells, game.spells):
        h, w = leftout.shape[:2]
        combine(leftout, spell, result, offset_h, offset_w)
        offset_w += w // scooch
    offset_w = 0
    offset_h += h_l
    return result
