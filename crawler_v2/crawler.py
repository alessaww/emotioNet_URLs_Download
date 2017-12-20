# --*0-- coding: utf-8 -*-
import asyncio
import aiohttp
import aiofiles
import time
import os
import logging

thread_sleep = 1  # 防爬虫，停顿1秒


class Crawler:
    def __init__(self, links, max_tries=4, max_tasks=10, loop=None, save_path='./', log_file='./log.txt'):
        self.loop = loop or asyncio.get_event_loop()
        self.links = links
        self.max_tries = max_tries
        self.max_tasks = max_tasks
        self.save_path = save_path
        self.log_file = log_file
        self.url_queue = asyncio.Queue(loop=self.loop)

        self.session = aiohttp.ClientSession(loop=self.loop, conn_timeout=3)  # 这里最好最好加上conn_time

        logging.basicConfig(level='INFO', filename=log_file, filemode='w', format='%(message)s')
        self.log = logging.getLogger()

    def close(self):
        self.session.close()

    async def work(self):
        try:
            while True:
                link = await self.url_queue.get()
                print('url队列数量: {}'.format(self.url_queue.qsize()))
                await self.fetch(link, self.url_queue.qsize())
                self.url_queue.task_done()
                await asyncio.sleep(thread_sleep)
        except asyncio.CancelledError:
            pass

    async def save_image(self, response, num):
        if response.status == 200:
            async with aiofiles.open(os.path.join(self.save_path, '{:07d}.jpg'.format(num)), 'wb') as f:
                await f.write(await response.read())
        else:
            print('RESPONSE ERROR {}:{}'.format(response.status, response.url))
            self.log.info('RESPONSE ERROR {}:{}'.format(response.status, response.url))
            return

    async def fetch(self, link, numbers):
        tries = 0
        while tries < self.max_tries:
            try:
                print('请求图片: {}'.format(link))
                response = await self.session.get(link)
                break
            except aiohttp.ClientError:
                pass
            tries += 1
        else:
            # 如果没有进入循环体，则执行此条语句
            print('connect error: {}'.format(link))
            self.log.info('CONNECTED ERROR:{}'.format(link))
            return
        try:
            await self.save_image(response, numbers)
            print('{} STORED AT {}'.format(response.url, os.path.join(self.save_path, '{:07d}.jpg'.format(numbers))))
        except Exception as e:
            print('Save Error! {}-{}'.format(e, link))
            self.log.info('SAVE ERROR:{}-{}'.format(e, link))
        finally:
            await response.release()

    async def run(self):
        start = time.time()
        print("Starting Download")
        await asyncio.wait([self.url_queue.put(link) for link in self.links])
        workers = [asyncio.ensure_future(self.work()) for _ in range(self.max_tasks)]
        await self.url_queue.join()
        for w in workers:
            w.cancel()
        end = time.time()
        print("Total Time: {}".format(end - start))

