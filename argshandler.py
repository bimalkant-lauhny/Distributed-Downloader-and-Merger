import sys

class ArgsHandler:
	''' Class for Command Line Arguments Handling Operations'''
	def __init__(self, args):
		self.url = None
		if not(len(args) == 2):
			print("No URL Provided! Exiting...")
			sys.exit()
		self.url = args[1]
		
	def get_download_url(self):
		return self.url
