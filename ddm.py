import urllib3
import logging
import os
import sys
import shutil
import threading
import pathlib
import socket
from argshandler import ArgsHandler
from filehandler import FileHandler

class DistributedDownloaderAndMerger(ArgsHandler, FileHandler):

	''' Main class providing interface of the software'''

	def __init__(self):
		ArgsHandler.__init__(self)
		FileHandler.__init__(self)
		logging.getLogger("urllib3").setLevel(logging.WARNING)

	# function for cleaning at program exit
	def final_clean(self, interrupted=False):
		self.delete_dir(self.args.tempdir)
		if interrupted == True:
			''' delete the partially downloaded file if user interrupted
			the download '''
			self.delete_file(self.filepath)

	# function for sending request and receiving response
	def make_request(self, headers=None):

		try:
			resp = self.http.request("GET", 
				self.args.url.replace("https", "http"), 
				retries=self.args.retries, 
				timeout=self.args.timeout,
				preload_content=False,
				headers=headers)
		except urllib3.exceptions.NewConnectionError:
			# if failed to create connection
			print ("Connection Failed!")
		except urllib3.exceptions.SSLError:
			# if failed to establish secure connection (https)
			print ("SSL Error!")

		return resp

	# function which acts as handler for download threads
	def seg_handler(self, tempfilepath, range_left, range_right):
		resp = self.make_request({'Range': 'bytes=%d-%d' % (range_left, range_right)})
		chunk_size = 1024 * 256 #256KB

		with open(tempfilepath, "wb") as fp:
			downloaded = 0 #in KBs
			while True:
				data = resp.read(chunk_size)
				if not data:
					print("\nDownload Finished.")
					break
				fp.write(data)
				downloaded += sys.getsizeof(data) 
				print ("\r{0:.2f} MB".format(downloaded/(1024*1024)), end="")

		resp.release_conn()

	# function to get a list of sizes to be downloaded by each thread
	def get_download_sizes_list(self):
		# no of bytes per thread
		size_per_thread = self.filesize//self.args.threads
		# stores size to be downloaded by each thread
		sizes_list = [size_per_thread] * self.args.threads
		# remaining size not assigned to any thread 
		rem = self.filesize % self.args.threads	
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
		for f in range(self.args.threads):
			# calling seg_handler() for each thread
			t = threading.Thread(target=self.seg_handler,
				kwargs={
				'tempfilepath': self.args.tempdir + "/temp" + str(f), 
				'range_left': ranges_list[f][0],
				'range_right': ranges_list[f][1]
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
			for f in range(self.args.threads):
				tempfilepath = self.args.tempdir + "/temp" + str(f)
				with open(tempfilepath, "rb") as fd:
					shutil.copyfileobj(fd, wfd)		
				# delete copied segment
				self.delete_file(tempfilepath)

	# function to perform file download
	def download(self):
		self.handle_args()

		if self.args.proxy:
			self.http = urllib3.ProxyManager(self.args.proxy)
		else:
			self.http = urllib3.PoolManager()

		#extracting filename from URL
		self.filename = os.path.basename(self.args.url).replace("%20", "_")

		# getting complete filepath
		self.filepath = self.args.dir + "/" + self.filename

		#making an initial request to get header information
		resp = self.make_request()

		# extracting the size of file to be downloaded in bytes, from header
		self.filesize = int(resp.headers['Content-Length'])

		# if server supports segmented download
		if self.range_download_support(resp):
			# get ranges for download for each thread
			ranges_list = self.get_download_ranges_list()
			# perform multithreaded download on single system
			self.multithreaded_download(ranges_list)
			# merge multithreaded download parts
			self.merge_multithreaded_download_parts()
		else:	
			print('''Server doesn't support multithreaded downloads!
				Download will be performed using single thread, on master system.''')	
			self.seg_handler(self.filepath, 
				0, 
				self.filesize-1)

		# perform final cleaning after download completion
		self.final_clean(interrupted=False)