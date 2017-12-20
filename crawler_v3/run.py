import os
import asyncio
from urllib.parse import urljoin
from downloader import Downloader
import random

BASE_URL_PATH = './emotioNet_URLs/emotioNet_3'
CURRENT_PATH = os.path.dirname(__file__)
BASE_SAVE_PATH = '/home/leo/Images/emotionNet_3'


def get_urls(links_file):
    # Any custom logic that represents list with links
    with open(links_file) as file:
        return (line.strip() for line in file.readlines())


def get_files(urls_path):
    file_list = os.listdir(urls_path)
    for f in file_list:
        _, fext = os.path.splitext(f)
        if fext != '.txt':
            file_list.remove(f)
    random.shuffle(file_list)
    return file_list


headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) "
                         "AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
           "Accept": "text/html,application/xhtml+xml,"
                     "application/xml;q=0.9,image/webp,*/*;q=0.8"}

if __name__ == '__main__':
    for links_file in get_files(BASE_URL_PATH):
        # oldloop = asyncio.get_event_loop()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop=loop)
        links = get_urls(os.path.join(BASE_URL_PATH, links_file))
        file_name, _ = os.path.splitext(links_file)
        save_path = os.path.join(BASE_SAVE_PATH, file_name)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        log_file = os.path.join(BASE_SAVE_PATH, file_name+'.log')
        downloader = Downloader(links, save_path, log_file, concurrency=50, headers=headers, streaming=True)
        try:
            loop.run_until_complete(downloader.run())
        except Exception:
            print('ERROR')
        finally:
            loop.stop()
            loop.run_forever()
            loop.close()
        # asyncio.set_event_loop(oldloop)
        print("==============================================================================================")
