import configparser

class PeerClientConfigHandler:
	"""Class for PeerClientConfigHandler"""
	def __init__(self):
		self.peer_server_port = None
		self.tracker_port 	  = None
		self.client_tracker_bind_port = None

	def parseConfig(self):
		config = configparser.ConfigParser()
		config.read('peer-client-config.ini')

		try:
			self.peer_server_port = config['CLIENT']['PEER_SERVER_PORT'];

		except KeyError:
			print ("No peer_server_port provided ")
			self.peer_server_port = 9000

		try:
			self.tracker_port = config['CLIENT']['TRACKER_PORT'];

		except KeyError:
			print ("No tracker_port provided ")
			self.tracker_port = 5000

		try:
			self.client_tracker_bind_port = config['LIENT']['CLIENT_TRACKER_BIND_PORT'];

		except KeyError:
			print ("No client_tracker_bind_port provided ")
			self.client_tracker_bind_port = 8000	

	def get_peer_server_port(self):
		return self.peer_server_port

	def get_tracker_port(self):
		return self.tracker_port

	def get_client_tracker_bind_port(self):	
		return self.client_tracker_bind_port
		



