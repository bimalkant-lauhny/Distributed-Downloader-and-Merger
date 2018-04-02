import argparse
import sys
import pathlib

class ArgsHandler:
	''' Class for Command Line Arguments Handling Operations'''
	def __init__(self):
		self.args = None
		
	# handles command line arguments
	def handle_args(self):

		parser = argparse.ArgumentParser()

		parser.add_argument("--url", 
			help="Enter the URL of the file (Required)")

		parser.add_argument("--proxy", 
			help='''Enter the proxy if required, 
			default = no proxy''')

		parser.add_argument("--dir", 
			help='''Enter the directory to store the downloaded file, 
			default = ~/Downloads/''')

		parser.add_argument("--tempdir", 
			help='''Enter the directory to store the temporary files, 
			default = ~/Downloads/.ddmtemp/''')

		parser.add_argument("--timeout", 
			help='''Enter the request timeout in seconds,
			default = 5.0''', 
			type=float)

		parser.add_argument("--retries", 
			help='''Enter the number of retries,
			default = 5''',
			type=int)

		parser.add_argument("--threads", 
			help='''Enter the number of threads,
			default = 2''',
			type=int)

		self.args = parser.parse_args()

		self.handle_default_args()

	# sets default arguments if not supplied by the user
	def handle_default_args(self):

		if not self.args.url:
			print("You didn't supply the download URL! See --help or -h for details.")	
			sys.exit()

		if not self.args.dir:
			self.args.dir = str(pathlib.Path.home()) + "/Downloads/"

		if not self.args.tempdir:
			self.args.tempdir = self.args.dir + "/.ddmtemp/" 
			# create temp directory
			self.create_dir(self.args.tempdir)

		if not self.args.timeout:
			self.args.timeout = 5.0	

		if not self.args.retries:
			self.args.retries = 5

		if not self.args.threads:
			self.args.threads = 2
