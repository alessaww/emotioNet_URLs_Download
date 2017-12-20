# -*- coding: utf-8 -*-
import asyncio
import aiohttp
import aiofiles
import time
import os

class Crawler:
	def __init__(self, 
		links,  # image urls
		headers = None,
		streaming = True,  # content type is file streaming
		download_to = './',  # which director to save downloaded images
		max_tries = 5,  # Per-ure limits
		max_tasks = 100, # Concurrence limits
		loop = None):
		self.loop = loop
		self.links = links
		self._is_streaming = streaming
		self.path = download_to
		self.max_tries = max_tries
		self.max_tasks = max_tasks
		self.queue = asyncio.Queue()
		self.session = aiohttp.ClientSession(loop=self.loop, headers= headers, conn_timeout=2, read_timeout=5)
		self.t0 = time.time()
		self.t1 = None

	def close(self):
		self.session.close()


	# 下载图片文件
	async def fetch_stream(self, url, save_path):
		tries = 0
		exception = None
		while tries < self.max_tries:
			try:
				print("get {0}...".format(url))
				response = await self.session.get(url, allow_redirects=False)
				print("")
				if tries > 1:
					print('try {} for {} success'.format(tries, url))
				break
			except aiohttp.ClientError as client_error:
				print('try {} for {} rasied {}'.format(tries, url, client_error))
				exception = client_error
			tries += 1
		else:
			print('{} failed after {} tries, exception:{}'.format(url, self.max_tries, exception))
			return

		try:
			if response.status != 200:
				print("DOWNLOAD ERROR:{}-{}".format(response.status, url))
			else:
				tmp = save_path + '.chunks'
				with open(tmp, 'ab') as file:
					while True:
						chunk = await response.content.read(1024)
						if not chunk:
							break
						file.write(chunk)
				os.rename(tmp, save_path)
				print('FILE HAS BEEN STORED AT {}'.format(save_path))
		except Exception:
			print('DOWNLOAD ERROR')
		finally:
			await response.release()


	# 下载文档
	async def fetch_content(self, url, save_path):
		pass


	async def worker(self):
		try:
			url = 'none'
			while True:
				url = await self.queue.get()
				# print('PROCESSING {}'.format(url))
				
				path = os.path.join(self.path, url.split('/')[-1])
				if not os.path.isdir(os.path.dirname(path)):
					os.makedirs(os.path.dirname(path))

				if self._is_streaming:
					await self.fetch_stream(url, path)
				else:
					await self.fetch_content(url, path)

				print('REMAINED {}'.format(self.queue.qsize()))
				self.queue.task_done()
		except asyncio.CancelledError:
			print('An error has occurred during downloading {}'.format(url))

	async def run(self):
		await asyncio.wait([self.queue.put(link) for link in self.links])
		tasks = [asyncio.ensure_future(self.worker()) for _ in range(self.max_tasks)]
		await self.queue.join()
		for task in tasks:
			task.cancel()
		self.session.close()

		# workers = [asyncio.Task(self.work(), loop=self.loop) for _ in range(self.max_tasks)]
		# print('Startiing downloading')
		# self.t0 = time.time()
		# await self.queue.join()
		# self.t1 = time.time()
		# for w in workers:
		# 	w.cancel()

