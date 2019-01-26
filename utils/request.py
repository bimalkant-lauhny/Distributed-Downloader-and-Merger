"""
	Handles requests
"""
import sys
import urllib3


class Request:
	"""Module for requests using urllib3"""
	def __init__(self):
		pass

	def make_request(self, url, retries=5, timeout=5, proxy=None, headers=None):
		""" function for sending request and receiving response """
		http = None
		print("Request Proxy: ", proxy)
		if proxy:
			http = urllib3.ProxyManager(proxy)
		else:
			http = urllib3.PoolManager()
		try:
			resp = http.request("GET", 
				url.replace("https", "http"), 
				retries=retries, 
				timeout=timeout,
				preload_content=False,
				headers=headers)
		except urllib3.exceptions.NewConnectionError:
			# if failed to create connection
			print ("Connection Failed!")
		except urllib3.exceptions.SSLError:
			# if failed to establish secure connection (https)
			print ("SSL Error!")

		return resp
	
	def download_range(self, url, filepath, range_left, range_right, proxy=None):
		""" download a file range """
		resp = self.make_request(url, proxy=proxy, headers={'Range': 'bytes=%d-%d' % (range_left, range_right)})
		chunk_size = 1024 * 256 #256KB

		with open(filepath, "wb") as fp:
			downloaded = 0 #in KBs
			while True:
				data = resp.read(chunk_size)
				if not data:
					print("\nDownload Finished.")
					break
				fp.write(data)
				downloaded += sys.getsizeof(data) 
				print ("\r{0:.2f} MB".format(downloaded/(1024*1024)), end="")

		self.close_connection(resp)	

	def close_connection(self, response):
		""" function for closing connection after download is complete """
		response.release_conn()
		