from tqdm import tqdm
import requests

def download_file(url):
    response = requests.get(url, stream=True)

    with open(url.split('/')[-1], "wb") as handle:
        for data in tqdm(response.iter_content(), desc=url):
            handle.write(data)

if __name__ == '__main__':
    download_file("http://api.hearthstonejson.com/v1/latest/enUS/cards.collectible.json")
    download_file("http://api.hearthstonejson.com/v1/latest/enUS/cards.json")
