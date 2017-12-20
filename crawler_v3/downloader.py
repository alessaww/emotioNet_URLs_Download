import time
import logging
import os
import asyncio
import aiohttp


class Downloader:
    def __init__(self, links, download_to, log_file, headers=None,
                 concurrency=10, streaming=False, verbose=True):

        self.links = links
        self.path = download_to
        self.log_file = log_file
        self.client = aiohttp.ClientSession(headers=headers, conn_timeout=10)
        self.queue = asyncio.Queue()
        self.concurrency = concurrency
        self._is_streaming = streaming
        self.sem = asyncio.Semaphore(1000)

        logging.basicConfig(level='INFO', filename=self.log_file, filemode='w')
        self.log = logging.getLogger()
        # if not verbose:
        #     self.log.disabled = True

    def close(self):
        self.client.close()

    async def download(self, url, path):
        async with self.client.get(url) as response:
            if response.status != 200:
                self.log.error('BAD RESPONSE: {}'.format(response.status))
                return
            content = await response.read()

        with open(path, 'wb') as file:
            file.write(content)

        self.log.info('File has been stored at {}'.format(path))

    async def stream_download(self, url, path):
        async with self.sem:
            async with self.client.get(url, allow_redirects=False) as response:
                if response.status != 200:
                    self.log.error('BAD RESPONSE: {}'.format(response.status))
                    return
                # Here we write file in blocking mode.
                # The only benefit here is that, memory consumed more carefully.
                tmp = path + '.chunks'
                with open(tmp, 'ab') as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        file.write(chunk)
                os.rename(tmp, path)
            self.log.info('FILE HAS BEEN STORED AT {}'.format(path))

    async def worker(self):
        self.log.info('Starting worker')
        while True:
            link = await self.queue.get()

            try:
                self.log.info('PROCESSING {}'.format(link))

                path = os.path.join(self.path, link.split('/')[-1])

                if not os.path.isdir(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))

                if not os.path.exists(path):
                    if self._is_streaming:
                        await self.stream_download(link, path)
                    else:
                        await self.download(link, path)
                    self.log.info('REMAINED {}'.format(self.queue.qsize()))
                    print('REMAINED {}'.format(self.queue.qsize()))
            except Exception:
                self.log.error('An error has occurred during downloading {}'.
                              format(link), exc_info=False)
            finally:
                self.queue.task_done()

    async def run(self):
        start = time.time()
        print('Starting downloading')
        await asyncio.wait([self.queue.put(link) for link in self.links])

        tasks = [asyncio.ensure_future(self.worker())
                 for _ in range(self.concurrency)]

        await self.queue.join()

        self.log.info('Finishing...')
        for task in tasks:
            task.cancel()

        self.client.close()

        end = time.time()
        print('FINISHED AT {} secs'.format(end-start))
