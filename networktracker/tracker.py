import socket
import threading

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


class PeerThread(threading.Thread):

	def __init__(self, tracker, peer, address):
		threading.Thread.__init__(self)
		self.tracker = tracker		
		self.peer = peer 
		self.address = address 

	def run(self):
		size = 1024 
		msg = self.peer.recv(size)
		if msg:
			msg = msg.decode()
			print("[+] Received Message: {}".format(msg))
			if (msg == "addme"):
				# peer-server wants to act as server
				self.tracker.addPeer(self.address)
				print("Updated trackers list: {}".format(self.tracker.getPeerServersList()))
				self.peer.shutdown(socket.SHUT_RDWR)
				self.peer.close()
				print("[-] Client Disconnected: {}".format(self.address))
			elif (msg == "sendpeerslist"):
				# peer-client needs peer-servers list to distribute the download
				response = self.tracker.getPeerServersList()
				response = str(response).encode()
				self.peer.sendall(response)
			elif (msg == "removeme"):
				# peer-server wants to leave the network
				self.tracker.removePeer(self.address)
				print("Updated trackers list: {}".format(self.tracker.getPeerServersList()))
				self.peer.shutdown(socket.SHUT_RDWR)
				self.peer.close()
				print("[-] Client Disconnected: {}".format(self.address))


class ThreadedTrackerServer:

    def __init__(self, tracker_server_address):
        self.tracker_server_address = tracker_server_address 
        self.tracker = NetTracker()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.tracker_server_address)

    def listen(self):
        self.sock.listen(5)
        print("[+] Listening for clients...")
        while True:
            peer, address = self.sock.accept()
            print("[+] Client Connected: {}".format(address))
            #client.settimeout(60)
            new_peer_thread = PeerThread(self.tracker, peer, address)
            new_peer_thread.daemon = True
            new_peer_thread.start()

    

if __name__ == "__main__":
	tracker_host = ''
	tracker_port = 5000
	tracker_server_address = (tracker_host, tracker_port)
	ThreadedTrackerServer(tracker_server_address).listen()