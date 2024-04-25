import os
import re

from tqdm import tqdm
import requests

def download_file(url, to='.'):
    response = requests.get(url, stream=True)

    with open(to + '/' + url.split('/')[-1], "wb") as handle:
        for data in tqdm(response.iter_content(), desc=f"Downloading {url.split('/')[-1]}"):
            handle.write(data)

def download_collectable(to):
    download_file("http://api.hearthstonejson.com/v1/latest/enUS/cards.collectible.json", to)

VERSION_RE = re.compile(r"\"/v1/(\d+)/all\"")

def check_version():
    response = requests.get('https://api.hearthstonejson.com/v1/latest/all/')
    match = VERSION_RE.search(response.text)
    if match is not None:
        return int(match.group(1))
    else:
        return None


if __name__ == '__main__':
    #download_file("http://api.hearthstonejson.com/v1/latest/enUS/cards.collectible.json")
    #download_file("http://api.hearthstonejson.com/v1/latest/enUS/cards.json")
    print(check_version())