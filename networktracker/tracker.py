import socket
import threading

class NetTracker:

	def __init__(self):
		self.node_set = set()

	def addNode(self, node):
		self.node_set.add(node)

	def removeNode(self, node):
		try:
			self.node_set.remove(node)
		except KeyError:
			print("{} is not in the list of connected nodes!".format(node))

	def getPeersList(self):
		# add code for refreshing connected peers
		return self.node_set



class ClientThread(threading.Thread):

	def __init__(self, tracker, client, address):
		threading.Thread.__init__(self)
		self.tracker = tracker		
		self.client = client
		self.address = address 

	def run(self):
		size = 1024 
		while True:
			msg = self.client.recv(size)
			if msg:
				msg = msg.decode()
				print("[+] Received Message: {}".format(msg))
				if (msg == "addme"):
					# peer wants to act as server
					self.tracker.addNode(self.address)
				elif (msg == "sendpeerslist"):
					# peer needs client lists to distribute the download
					response = self.tracker.getPeersList()
					response = str(response).encode()
					self.client.sendall(response)
				elif (msg == "removeme"):
					# peer wants to leave the network
					self.tracker.removeNode(self.address)
					self.client.send("done".encode())
					self.client.close()
					print("[-] Client Disconnected: {}".format(self.address))
					break


class ThreadedServer:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_address = (self.host, self.port)
        self.tracker = NetTracker()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.server_address)

    def listen(self):
        self.sock.listen(5)
        print("[+] Listening for clients...")
        while True:
            client, address = self.sock.accept()
            print("[+] Client Connected: {}".format(address))
            #client.settimeout(60)
            new_client_thread = ClientThread(self.tracker, client, address)
            #new_client_thread.daemon = True
            new_client_thread.start()

    

if __name__ == "__main__":
	tracker_port = 5000
	ThreadedServer('', tracker_port).listen()