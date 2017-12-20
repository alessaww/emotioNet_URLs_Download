# --*0-- coding: utf-8 -*-
import asyncio
import os
import sys
from crawler import Crawler

CURRENT_PATH = os.path.dirname(__file__)  # 当前路径
URLS_PATH = os.path.join(CURRENT_PATH, 'emotioNet_URLs')  # urls 文件目录
BASE_SAVE_PATH = '/mnt/F/emotioNet_Database'  # 图片保存根路径
if not os.path.exists(BASE_SAVE_PATH):
    os.makedirs(BASE_SAVE_PATH)

BASE_LOG_PATH = os.path.join(CURRENT_PATH, 'download_logs')  # 日志保存路径
if not os.path.exists(BASE_LOG_PATH):
    os.makedirs(BASE_LOG_PATH)

log_file = os.path.join(os.path.dirname(__file__), './download.log')

# urls_file = 'test_urls.txt'

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) "
                         "AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
           "Accept": "text/html,application/xhtml+xml,"
                         "application/xml;q=0.9,image/webp,*/*;q=0.8"}


def get_urls(urls_file):
    with open(urls_file) as f:
        return (url.strip('\n') for url in f.readlines())


def get_file_list(urls_path):
    file_list = os.listdir(urls_path)
    for f in file_list:
        _, fext = os.path.splitext(f)
        if fext != '.txt':
            file_list.remove(f)
    return [os.path.join(URLS_PATH, f) for f in sorted(file_list)]


if __name__ == "__main__":
    for file in get_file_list(URLS_PATH):
        # ----------- 日志文件命名 -----------
        tmp = os.path.basename(file)
        name, ext = os.path.splitext(tmp)
        log_file = os.path.join(BASE_LOG_PATH, 'log_{}.log'.format(name))
        # ----------------------------------
        links = get_urls(file)  # 获取url生成器

        # --------------文件保存路径----------
        save_path = os.path.join(BASE_SAVE_PATH, name)
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        # ----------------------------------

        loop = asyncio.get_event_loop()
        crawler = Crawler(links=links, max_tries=4, max_tasks=50, save_path=save_path, log_file=log_file)
        try:
            loop.run_until_complete(crawler.run())
        except KeyboardInterrupt:
            sys.stderr.flush()
        finally:
            crawler.close()

            # -------- 这个地方要尤其注意，一定要加上loop.stop() -----------------
            # next two lines are required for actual aiohttp resource cleanup
            loop.stop()
            # ---------------------------------------------------------------
            loop.run_forever()

            loop.close()

        print('DONE!')