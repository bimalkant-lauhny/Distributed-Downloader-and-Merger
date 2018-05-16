import configparser
import pathlib

class PeerClientConfigHandler:
	"""Class for PeerClientConfigHandler"""
	def __init__(self):
		self.peer_server_port = None
		self.tracker_host = None
		self.tracker_port = None
		self.client_tracker_bind_port = None
		self.temp_dir = None

	def parseConfig(self):
		config = configparser.ConfigParser()
		config.read('peer-client-config.ini')

		try:
			self.peer_server_port = int(config['CLIENT']['PEER_SERVER_PORT'])

		except KeyError:
			print ("No peer_server_port provided!")
			self.peer_server_port = 9000

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
			self.proxy = config['CLIENT']['PROXY']
		except KeyError:
			print ("No proxy provided!")
			self.proxy = None

	def getPeerClientPort(self):
		return self.peer_server_port

	def getTrackerPort(self):
		return self.tracker_port

	def getTrackerHost(self):
		return self.tracker_host

	def getClientTrackerBindPort(self):	
		return self.client_tracker_bind_port

	def getTempDirPath(self):
		return self.temp_dir

	def getProxy(self):
		return self.proxy
		



