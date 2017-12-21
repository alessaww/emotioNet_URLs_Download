# -*- coding: utf-8 -*-
import asyncio
import aiohttp
import aiofiles
import time
import os


class Downloader:
    def __init__(self, links, download_to, log_file, max_tries=4, max_tasks=10,
                  max_sem=100, conn_timeout=10, headers=None, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.links = links
        self.download_to = download_to
        self.log_file = log_file

        self.max_tries = max_tries
        self.max_tasks = max_tasks
        self.sem = asyncio.Semaphore(max_sem)
        self.headers = headers

        self.queue = asyncio.Queue(loop=self.loop)
        self.session = aiohttp.ClientSession(loop=self.loop, headers=headers, conn_timeout=conn_timeout)

    def close(self):
        self.session.close()

    @staticmethod
    def rename(url):
        exts = ['.jpg', '.png', 'jif', '.bmp', 'jpeg']
        name = url.strip('\n').split('/')[-1]
        fname, ext = os.path.splitext(name)
        if ext.lower() in exts:
            ext = ext.lower()
        elif ext[:4].lower() in exts:
            ext = ext[:4].lower()
        elif ext[:5].lower() in exts:
            ext = ext[:5].lower()
        else:
            ext = '.jpg'
        return '{}{}'.format(fname, ext)

    async def download(self, url, save_path):
        async with self.sem:
            tries = 0
            while tries < self.max_tries:
                try:
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            async with aiofiles.open(save_path, 'wb') as f:
                                await f.write(await response.read())
                    break
                except aiohttp.ClientError as client_error:
                    pass
                tries += 1
            else:
                print("try {} times but still unconnected".format(self.max_tries))
                async with aiofiles.open(self.log_file, 'a') as log:
                    await log.write(url+'\n')

    async def worker(self):
        while True:
            url = await self.queue.get()
            print("processing {}".format(url))
            save_name = self.rename(url)
            try:
                save_path = os.path.join(self.download_to, save_name)
                await self.download(url, save_path)
                print('save successed {} to {}'.format(url, save_path))
                print('remained {}'.format(self.queue.qsize()))
            except Exception as e:
                print('save error. except: {}, url: {}'.format(e, url))
            finally:
                self.queue.task_done()

    async def run(self):
        start = time.time()
        print("Starting ...")
        await asyncio.wait([self.queue.put(link) for link in self.links])
        tasks = [asyncio.ensure_future(self.worker()) for _ in range(self.max_tasks)]
        await self.queue.join()
        for task in tasks:
            task.cancle()
        self.close()
        end = time.time()
        print("FINISED AT {} secs".format(end - start))