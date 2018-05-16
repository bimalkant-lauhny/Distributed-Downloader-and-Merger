import configparser

class PeerServerConfigHandler:
	"""Class for PeerServerConfigHandler"""
	def __init__(self):
		self.peer_server_port = None
		self.tracker_port = None
		self.server_tracker_bind_port = None

	def parseConfig(self):
		config = configparser.ConfigParser()
		config.read('peer-server-config.ini')
			
		try:
			self.peer_server_port = config['SERVER']['PEER_SERVER_PORT']
		except KeyError:
			print ("No peer_server_port provided")
			self.peer_server_port = 6000

		try:
			self.tracker_port = config['SERVER']['TRACKER_PORT']
		except KeyError:
			print ("No tracker_port provided ")
			self.tracker_port = 5000

		try:
			self.server_tracker_bind_port = config['SERVER']['SERVER_TRACKER_BIND_PORT']
		except KeyError:
			print ("No server_tracker_bind_port provided ")
			self.server_tracker_bind_port = 6000

	def get_peer_server_port(self):
		return self.peer_server_port

	def get_tracker_port(self):
		return self.tracker_port

	def get_server_tracker_bind_port(self):	
			return self.server_tracker_bind_port

				