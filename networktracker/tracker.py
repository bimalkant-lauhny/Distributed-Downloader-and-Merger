import sys
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
            peer_conn, peer_addr = self.sock.accept()
            print("[+] Peer Connected: {}".format(peer_addr))
            #client.settimeout(60)
            new_peer_thread = PeerThread(self.tracker, peer_conn, peer_addr)
            #new_peer_thread.daemon = True
            new_peer_thread.start()

    def stop_server(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        print("[-] Stopped Tracker Server.")

if __name__ == "__main__":
    tracker_host = ''
    tracker_port = 5000
    tracker_server_address = (tracker_host, tracker_port)

    try:
        server = ThreadedTrackerServer(tracker_server_address)
        server.listen()

    except:
        print("Oops!", sys.exc_info()[0], "occured...")

    finally:

        main_thread = threading.current_thread()
        for t in threading.enumerate():
            if t is main_thread:
                continue
            t.close_connection()

        server.stop_server()
