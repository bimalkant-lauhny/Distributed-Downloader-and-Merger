import configparser
import pathlib

class ConfigHandler:

	''' Class for parsing config.ini settings'''
	
	def __init__(self):
		self.download_dir = None
		self.temp_dir = None
		self.proxy = None
		self.threads = None
		self.timeouts = None
		self.retries = None

	def parse_config(self):
		config = configparser.ConfigParser()
		config.read('config.ini')

		try:
			self.download_dir = config['USER']['DOWNLOAD_DIR'] 
		except KeyError:
			print("No download directory provided! Setting default to ~/Downloads.")	
			self.download_dir = str(pathlib.Path.home()) + "/Downloads/"

		try:
			self.temp_dir = config['USER']['TEMP_DIR']
		except KeyError:
			print("No Temporary Directory provided! Setting default to DOWNLOAD_DIR/.ddmtemp/")
			self.temp_dir = self.download_dir + "/.ddmtemp/" 

		try:
			self.proxy = config['USER']['PROXY']
		except KeyError:
			print("No Proxy provided! Setting default to None.")

		try:
			self.threads = int(config['USER']['THREADS'])
		except KeyError:
			print("Number of download threads are not specified! Setting default to 4 threads")	
			self.threads = 4 

		try:
			self.timeouts = float(config['USER']['TIMEOUTS'])
		except KeyError:
			print("No Timeouts specified! Setting default to 5.0")	
			self.timeouts = 5.0 

		try:
			self.retries = int(config['USER']['RETRIES'])
		except KeyError:
			self.retries = 5 
			print("Number of retries not specified! Setting default to 5 times.")	

	''' Getter Functions for class attributes'''
	def get_download_dir(self):
		return self.download_dir

	def get_temp_dir(self):
		return self.temp_dir

	def get_proxy(self):
		return self.proxy

	def get_threads(self):
		return self.threads

	def get_retries(self):
		return self.retries

	def get_timeouts(self):
		return self.timeouts
