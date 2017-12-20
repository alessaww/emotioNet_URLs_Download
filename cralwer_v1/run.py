# -*- coding: utf-8 -*-

import asyncio
import aiohttp
import aiofiles
import os
import sys
from crawler import Crawler


URLS_PATH = '/home/leo/MyCodes/FER/emotioNet_URLs'  # url files directory
SAVE_PATH = os.path.join(os.path.dirname(__file__), 'IMAGES')  # images will download into the director
TEST_FILE = './url_list.txt'  # There are 1,000 urls in this file

if not os.path.exists(SAVE_PATH):
	os.mkdir(SAVE_PATH)

user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
headers={"User-Agent":user_agent}

def get_txtfiles(urls_path):
	files = os.listdir(urls_path)
	for file in files:
		name, ext = os.path.splitext(file)
		if ext != '.txt':
			files.remove(file)
	return sorted(files)


def get_urls(url_file):
	with open(url_file) as file:
		return (line.strip('\n') for line in file.readlines())



if __name__ == '__main__':
	# # ----------- test get_txtfiles ----------------
	# file_list = get_txtfiles(URLS_PATH)
	# print(file_list)

	# # ----------------------------------------------

	# ------------- test get_urls --------------------
	urls = get_urls(TEST_FILE)
	# for url in urls:
	# 	print(url)
	# ------------------------------------------------

	loop = asyncio.get_event_loop()

	crawler = Crawler(links=urls, download_to=SAVE_PATH, headers=headers, loop=loop)
	try:
		loop.run_until_complete(crawler.run())
	except KeyboardInterrupt:
		sys.stderr.flush()
		print('\nInterrupted\n')
	finally:
		crawler.close()
		loop.stop()
		loop.run_forever()
		loop.close()