import urllib3
import logging
import os
import sys
import shutil
import threading
import pathlib
from filehandler import FileHandler
from downloader import Downloader
from calculation import Calculation

class MultithreadedDownloader:

	"""Main class providing interface of the software"""

	def __init__(self):
		self.filehandle = FileHandler()
		self.download_handle = Downloader()
		self.calculate = Calculation()
		self.url = None 
		self.range_left = None
		self.range_right = None
		self.proxy = None 
		self.temp_dir = None 
		self.threads = None 
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
	def download(self, url, range_left, range_right, filename, filepath, 
				filesize, temp_dir, response, threads, proxy=None):

		self.url = url
		self.range_right = range_right
		self.range_left = range_left
		self.filename = filename
		self.filesize = filesize
		self.filepath = filepath		
		self.temp_dir = temp_dir
		self.threads = threads
		self.proxy = proxy

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