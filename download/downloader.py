# -*- coding: utf-8 -*-
import asyncio
import aiohttp
import aiofiles
import os
import logging
import time


class Downloader:
    def __init__(self, links, download_to, log_file, headers=None,
                 max_tasks=10, max_tries=4, max_sem=1000, streaming=True,
                 conn_time=5, loop=None):
        """

        :param links: 需要下载的链接
        :param download_to: 图片保存路径
        :param log_file: 下载日志，下载失败的链接保存在此文件
        :param headers: request headers,防爬虫
        :param max_tasks: 最大并行数
        :param max_tries: 请求最大重试次数
        :param streaming: 默认为True，下载图片
        :param max_sem:
        :param conn_time: 请求最大时间
        """
        self.loop = loop
        self.links = links
        self.download_to = download_to
        self.log_file = log_file
        self.headers = headers

        self.max_tasks = max_tasks
        self.max_tries = max_tries
        self.streaming = True

        self.queue = asyncio.Queue(loop=self.loop)
        self.client = aiohttp.ClientSession(loop=self.loop, headers=headers, conn_timeout=conn_time)
        self.sem = asyncio.Semaphore(max_sem)
        self._is_streaming = streaming

    def close(self):
        """
        关闭session
        :return:
        """
        self.client.close()

    async def download(self, url, path):
        """
        爬取网页时使用此函数
        :param url:
        :param path:
        :return:
        """
        pass

    """
    Creating a client session outside of coroutine
    client_session: <aiohttp.client.ClientSession object at 0x7fa28137fdd8>
    """
    async def stream_download(self, url, path):
        """
        爬取媒体文件时，使用此函数
        :param url: 图片url
        :param path: 文件保存路径
        :return:
        """
        async with self.sem:
            tries = 0
            while tries < self.max_tries:
                try:
                    response = await self.client.get(url, allow_redirects=False)
                    if tries > 1:
                        print("TRY {} FOR {} SUCCESS".format(tries, url))
                        break
                except aiohttp.ClientError as ce:
                    print("CLIENT ERROR {}".format(ce))  # 如果请求发生错误，重试
                tries += 1
            else:
                print("CONNECTED ERROR!{}".format(url))  # 如果连接失败，则停止连接
                async with aiofiles.open(self.log_file, 'a') as log:
                    await log.write("CONNECTED ERROR:{}\n".format(url))
                return

            if response.status == 200:
                try:
                    tmp = path + '.chunks'
                    with open(tmp, 'ab') as file:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            file.write(chunk)
                    os.rename(tmp, path)
                    print("SAVE SUCCESSED AT {}".format(path))
                except Exception as e:
                    print("SAVE ERROR {}:{}".format(e, url))
                finally:
                    response.release()
            else:
                print("RESPONSE ERROR {}:{}".format(response.status, url))
                async with aiofiles.open(self.log_file, 'a') as log:
                    await log.write("RESPONSE ERROR {}:{}\n".format(response.status, url))

    async def work(self):
        while True:
            link = await self.queue.get()
            try:
                path = os.path.join(self.download_to, link.split('/')[-1])

                if self._is_streaming:
                    await self.stream_download(link, path)
                else:
                    await self.download(link, path)

                print('REMAINED {}'.format(self.queue.qsize()))
            except Exception as de:
                print("An Error Has Occurred During Downloading {}:{}".format(de, link))
            finally:
                self.queue.task_done()

    async def run(self):
        start = time.time()
        print("Beginning Download")
        await asyncio.wait([self.queue.put(link) for link in self.links])
        tasks = [asyncio.ensure_future(self.work()) for _ in range(self.max_tasks)]
        await self.queue.join()
        for task in tasks:
            task.cancle()
        self.close()
        end = time.time()
        print("FINISED AT {} secs".format(end - start))

