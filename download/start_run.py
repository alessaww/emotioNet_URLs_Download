# -*- coding: utf-8 -*-
import asyncio
import os
from download.downloader import Downloader
import aiofiles

BASE_URL_PATH = '../emotioNET_URLs'
BASE_SAVE_PATH = '../IMAGES'
BASE_LOGS_PATH = '../log_files'


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
    return file_list


headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) "
                         "AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
           "Accept": "text/html,application/xhtml+xml,"
                     "application/xml;q=0.9,image/webp,*/*;q=0.8"}


if __name__ == '__main__':
    urls_file = 'emotioNet_1.txt'
    links = get_urls(os.path.join(BASE_URL_PATH, urls_file))

    loop = asyncio.get_event_loop()
    f_name, ext = os.path.splitext(urls_file)
    save_path = os.path.join(BASE_SAVE_PATH, f_name)

    if not os.path.exists(save_path):
        os.makedirs(save_path)
    log_file = os.path.join(BASE_LOGS_PATH, f_name+'.log')
    downloader = Downloader(links, save_path, log_file, headers, max_tasks=150,
                            max_tries=4, max_sem=1000, conn_time=30, loop=loop)

    try:
        loop.run_until_complete(downloader.run())
    except Exception as e:
        print(e)
    finally:
        loop.stop()
        loop.run_forever()
        loop.close()
