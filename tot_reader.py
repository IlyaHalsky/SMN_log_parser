import os
import shutil

import cv2
import numpy as np
import requests

from minions_utils import minions_by_id, cards_by_id
from smn_logs import read_log_file

def print_minion(m):
    return f"{m.card_id} ({m.attack_change}/{m.health_change}/{m.cost_change})"

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

if __name__ == '__main__':
    minions = read_log_file("last_game/ToT.log")
    count = 0
    last = None
    pairs = []
    for k, v in minions.items():
        if len(v.card_id) > 0 and not v.child_card and v.card_id in cards_by_id:
            if count == 0:
                last = v
                count = 1
            else:
                count = 0
                if v.dbf_id < last.dbf_id:
                    v.color[1] = 255
                else:
                    last.color[1] = 255
                print(print_minion(v), print_minion(last))
                pairs.append((v, last))
    image_pairs = []
    for a, b in pairs:
        image_pairs.append((en_image(a), en_image(b)))

    pair_width, pair_height = 0,0
    for a, b in image_pairs:
        pair_width = max(pair_width, a.shape[1] + b.shape[1])
        pair_height = max(max(a.shape[0], b.shape[0]),pair_height)
    pair_width += 100
    pair_height += 50
    result = np.zeros((pair_height * 5, pair_width * 10, 4), dtype=np.uint8)
    print(result.shape)
    v_offset = 0
    h_offset = 0
    count = 0
    for a, b in pairs:
        print(v_offset, h_offset, count)
        a_image = en_image(a)
        combine(a_image, a, result, v_offset, h_offset)
        b_image = en_image(b)
        combine(b_image, b, result, v_offset, h_offset+a_image.shape[1])
        text = f"{a.attack_change}/{a.health_change}/{a.cost_change}"
        font = cv2.FONT_HERSHEY_PLAIN
        scale = 4
        thickness = 2
        textsize = cv2.getTextSize(text, font , scale, thickness)[0]
        result = cv2.putText(
            result, text, (h_offset + a_image.shape[1] // 2 - textsize[0] // 2, v_offset + a_image.shape[0]+ 10), font ,
            scale, (255, 255, 255, 255), thickness, cv2.LINE_AA
        )
        text = f"{b.attack_change}/{b.health_change}/{b.cost_change}"
        textsize = cv2.getTextSize(text, font , scale, thickness)[0]
        result = cv2.putText(
            result, text, (h_offset + b_image.shape[1] // 2 - textsize[0] // 2 + a_image.shape[1], v_offset + b_image.shape[0] + 10),font,
            scale, (255, 255, 255, 255), thickness, cv2.LINE_AA
        )
        count += 1
        if count == 10:
            count = 0
            h_offset = 0
            v_offset += pair_height
        else:
            h_offset += pair_width
    cv2.imwrite("result.jpg", result)
