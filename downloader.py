from request import Request

class Downloader:
	""" class for downloading files"""

	def __init__(self):
		pass

	def download(self, url, filepath, range_left, range_right, proxy=None):
		req = Request()
		resp = req.makeRequest(url, headers={'Range': 'bytes=%d-%d' % (range_left, range_right)})
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

		req.closeConnection(resp)	