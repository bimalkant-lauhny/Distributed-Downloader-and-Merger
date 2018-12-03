class NetTracker:

	def __init__(self):
		self.peer_servers_set = set()

	def addPeer(self, peer_server):
		self.peer_servers_set.add(peer_server)

	def removePeer(self, peer_server):
		try:
			self.peer_servers_set.remove(peer_server)
		except KeyError:
			print("{} is not in the list of connected peers!".format(peer_server))

	def getPeerServersList(self):
		# add code for refreshing connected peers
		return self.peer_servers_set