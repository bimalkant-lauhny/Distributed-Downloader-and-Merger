import configparser
import pathlib

class PeerClientConfigHandler:
	"""Class for PeerClientConfigHandler"""
	def __init__(self):
		self.client_server_bind_port = None
		self.tracker_host = None
		self.tracker_port = None
		self.client_tracker_bind_port = None
		self.proxy = None
		self.threads = None
		self.temp_dir = None
		self.download_dir = None

	def parseConfig(self):
		config = configparser.ConfigParser()
		config.read('peer-client-config.ini')

		try:
			self.client_server_bind_port = int(config['CLIENT']['CLIENT_SERVER_BIND_PORT'])

		except KeyError:
			print ("No peer_server_port provided!")
			self.client_server_bind_port = 8000

		try:
			self.tracker_port = int(config['CLIENT']['TRACKER_PORT'])

		except KeyError:
			print ("No tracker_port provided!")
			self.tracker_port = 5000

		try:
			self.tracker_host = config['CLIENT']['TRACKER_HOST']
		except KeyError:
			print ("No tracker_host provided!")
			self.tracker_host = '' 

		try:
			self.client_tracker_bind_port = int(config['CLIENT']['CLIENT_TRACKER_BIND_PORT'])

		except KeyError:
			print ("No client_tracker_bind_port provided!")
			self.client_tracker_bind_port = 8000	

		try:
			self.temp_dir = config['CLIENT']['TEMP_DIR'] + '/'
		except KeyError:
			print ("No temp_dir provided!")
			self.temp_dir = str(pathlib.Path.home()) + "/Downloads/client-temp/"

		try:
			self.download_dir = config['CLIENT']['DOWNLOAD_DIR'] 
		except KeyError:
			print("No download directory provided! Setting default to ~/Downloads.")	
			self.download_dir = str(pathlib.Path.home()) + "/Downloads/"

		try:
			self.proxy = config['CLIENT']['PROXY']
		except KeyError:
			print ("No proxy provided!")
			self.proxy = None

		try:
			self.threads = int(config['CLIENT']['THREADS'])
		except KeyError:
			print("Number of download threads are not specified! Setting default to 4 threads.")	
			self.threads = 4 

	def getClientServerBindPort(self):
		return self.client_server_bind_port

	def getTrackerPort(self):
		return self.tracker_port

	def getTrackerHost(self):
		return self.tracker_host

	def getClientTrackerBindPort(self):	
		return self.client_tracker_bind_port

	def getTempDirPath(self):
		return self.temp_dir

	def getDownloadDirPath(self):
		return self.download_dir

	def getProxy(self):
		return self.proxy

	def getNumThreads(self):
		return self.threads
		



