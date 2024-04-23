import os
import shutil

import requests
from tqdm import tqdm

from minions_utils import minions_by_id

if __name__ == '__main__':
    for key in tqdm(minions_by_id.keys()):
        url = f"https://art.hearthstonejson.com/v1/render/latest/enUS/256x/{key}.png"
        if not os.path.exists("./image_cache"):
            os.makedirs(f"./image_cache")
        if not os.path.exists(f"./image_cache/{key}.png"):
            response = requests.get(url, stream=True)
            with open(f"./image_cache/{key}.png", 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response