import urllib3
import logging
import os
import sys
import shutil
import threading
import pathlib
from filehandler import FileHandler
from request import Request
from downloader import Downloader
from calculation import Calculation

class MultithreadedDownloader:

	"""Main class providing interface of the software"""

	def __init__(self, url, proxy, temp_dir, download_dir, threads):
		self.filehandle = FileHandler()
		self.req_handle = Request()
		self.download_handle = Downloader()
		self.calculate = Calculation()
		self.url = url
		self.proxy = proxy
		self.temp_dir = temp_dir
		self.download_dir = download_dir
		self.threads = threads
		self.http = None
		self.filepath = None
		self.filesize = None
		self.filename = None
		logging.getLogger("urllib3").setLevel(logging.WARNING)

	# function for cleaning at program exit
	def final_clean(self, interrupted=False):
		self.filehandle.deleteDir(self.temp_dir)
		if interrupted == True:
			''' delete the partially downloaded file if user interrupted
			the download '''
			self.filehandle.deleteFile(self.filepath)

	# function to get a list of sizes to be downloaded by each thread
	def get_download_sizes_list(self):
		# no of bytes per thread
		size_per_thread = self.filesize//self.threads
		# stores size to be downloaded by each thread
		sizes_list = [size_per_thread] * self.threads 
		# remaining size not assigned to any thread 
		rem = self.filesize % self.threads	
		# loop to equally assign sizes to download, to each thread
		index = 0
		while rem != 0:
			sizes_list[index] += 1
			rem -= 1
			index += 1

		return sizes_list

	# function to get a list of ranges to be downloaded by each thread
	def get_download_ranges_list(self):

		sizes_list = self.get_download_sizes_list()
		sizes_list.insert(0, 0)

		index = 2 
		while index < len(sizes_list):
			sizes_list[index] += sizes_list[index - 1]
			index += 1

		# list storing tuples of byte-ranges
		ranges_list = []
		index = 1
		while index < len(sizes_list):
			ranges_list.append((sizes_list[index - 1],sizes_list[index] - 1))
			index += 1

		return ranges_list

	# returns boolean value indicating support for range downloading
	def range_download_support(self, resp):
		try:
			supported = (resp.headers['Accept-Ranges'] == 'bytes')
		except KeyError:
			supported = False

		return supported

	# function to perform multithreaded download
	def multithreaded_download(self, ranges_list):
		# downloading each segment
		for f in range(self.threads):
			# calling Downloader.download_range() for each thread
			t = threading.Thread(target=self.download_handle.download_range,
				kwargs={
				'url': self.url,
				'filepath': self.temp_dir + "/temp" + str(f), 
				'range_left': ranges_list[f][0],
				'range_right': ranges_list[f][1],
				'proxy': self.proxy
				})
			t.setDaemon(True)
			t.start()	

		# except main_thread, calling join() for each thread
		# it ensures that merging of parts occur only after each thread has completed downloading
		main_thread = threading.current_thread()
		for t in threading.enumerate():
			if t is main_thread:
				continue
			t.join()	

	# function to perform merging of parts performed by multiple threads on single system
	def merge_multithreaded_download_parts(self):
		# merging parts
		with open(self.filepath,'wb') as wfd:
			for f in range(self.threads):
				tempfilepath = self.temp_dir + "/temp" + str(f)
				with open(tempfilepath, "rb") as fd:
					shutil.copyfileobj(fd, wfd)		
				# delete copied segment
				self.filehandle.deleteFile(tempfilepath)

	# function to perform file download
	def download(self):
		if self.proxy:
			self.http = urllib3.ProxyManager(self.proxy)
		else:
			self.http = urllib3.PoolManager()

		# make sure that download path and temp directory exists
		self.filehandle.createDir(self.download_dir)
		self.filehandle.createDir(self.temp_dir)

		# extracting filename from URL
		self.filename = os.path.basename(self.url.replace("%20", "_"))

		# getting complete filepath
		self.filepath = self.download_dir + "/" + self.filename

		#making an initial request to get header information
		response = self.req_handle.makeRequest(
									url=self.url,
									proxy=self.proxy)

		# extracting the size of file to be downloaded in bytes, from header
		self.filesize = int(response.headers['Content-Length'])

		# if server supports segmented download
		if self.range_download_support(response):
			# get ranges for download for each thread
			ranges_list = self.calculate.getDownloadRangesList(0, 
															self.filesize-1, 
															self.threads)
			# perform multithreaded download on single system
			self.multithreaded_download(ranges_list)
			# merge multithreaded download parts
			self.merge_multithreaded_download_parts()
		else:	
			print('''Server doesn't support multithreaded downloads!
				Download will be performed using single thread, on master system.''')	
			self.download_handle.download_range(self.url,
										self.filepath,
										0, 
										self.filesize-1,
										self.proxy)

		# perform final cleaning after download completion
		self.final_clean(interrupted=False)