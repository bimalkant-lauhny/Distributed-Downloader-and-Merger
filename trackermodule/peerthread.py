import threading
import socket

class PeerThread(threading.Thread):

	def __init__(self, tracker, peer_conn, peer_addr):
		threading.Thread.__init__(self)
		self.tracker = tracker		
		self.peer_conn = peer_conn
		self.peer_addr = peer_addr 

	def run(self):
		size = 1024 
		msg = self.peer_conn.recv(size)
		if msg:
			msg = msg.decode()
			print("[+] Received Message: {}".format(msg))
			if (msg == "addme"):
				# peer-server wants to act as server
				self.tracker.addPeer(self.peer_addr)
				print("Updated trackers list: {}".format(self.tracker.getPeerServersList()))
				self.close_connection()
				print("[-] Peer Server Added to List: {}".format(self.peer_addr))
			elif (msg == "sendpeerslist"):
				# peer-client needs peer-servers list to distribute the download
				response = self.tracker.getPeerServersList()
				if len(response) == 0:
					response = "None"
				response = str(response).encode()
				self.peer_conn.sendall(response)
				print("[+] Sent Peer Servers List to: {}".format(self.peer_addr))
				self.close_connection()
			elif (msg == "removeme"):
				# peer-server wants to leave the network
				self.tracker.removePeer(self.peer_addr)
				print("Updated trackers list: {}".format(self.tracker.getPeerServersList()))
				self.close_connection()
				print("[-] Peer Server removed from List: {}".format(self.peer_addr))

	def close_connection(self):
		self.peer_conn.shutdown(socket.SHUT_RDWR)
		self.peer_conn.close()
		print ("[-] Closed Connection with {}.".format(self.peer_addr))