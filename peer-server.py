import sys
import socket
import threading
import json

class PeerClientThread(threading.Thread):

    def __init__(self, client, address):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address 

    def run(self):
        size = 1024 
        # receive {"url":"", "range-left":"", "range-right":""} from client
        msg = self.client.recv(size)
        if msg:
            msg = msg.decode()
            print("[+] Received Message: {}".format(msg))
            msg = json.loads(msg)
            self.client.close()
            print("[-] Client Disconnected: {}".format(self.address))

class ThreadedPeerServer:

    def __init__(self, server_address):
        self.server_address = server_address 
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.server_address)

    def registerWithTracker(self, tracker_server_address, bind_port):
        # connect to tracker
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', bind_port))
        s.connect(tracker_server_address)
        print("[+] Connected with Tracker.")
        # register the peer-server
        s.send("addme".encode())
        print("[+] Sent addme request.")
        # close the connection to tracker       
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        print("[-] Disconnected with Tracker.")

    def listen(self):
        self.sock.listen(5)
        print("[+] Listening for clients...")
        while True:
            client, address = self.sock.accept()
            print("[+] Client Connected: {}".format(address))
            #client.settimeout(60)
            new_client_thread = PeerClientThread(client, address)
            new_client_thread.daemon = True
            new_client_thread.start()

    def unregisterWithTracker(self, tracker_server_address, bind_port):
        # connect to tracker
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', bind_port))
        s.connect(tracker_server_address)
        print("[+] Connected with Tracker.")
        # unregister the peer-server
        s.send("removeme".encode())
        print("[+] Sent removeme request.")
        # close the connection to tracker       
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        print("[-] Disconnected with Tracker.")

if __name__ == '__main__':
    tracker_host = ''
    tracker_port = 5000
    tracker_server_address = (tracker_host, tracker_port)
    peer_server_host = ''
    peer_server_port = 6000
    peer_server_address = (peer_server_host, peer_server_port)
    bind_port = 7000 # port to which peer-server is bound while communicating with tracker-server
    server = None
    try:
        server = ThreadedPeerServer(peer_server_address)
        server.registerWithTracker(tracker_server_address, bind_port)
        server.listen()
    except:
        print("Oops!",sys.exc_info()[0],"occured.") 
    finally:
        server.unregisterWithTracker(tracker_server_address, bind_port)
        # exit
        sys.exit(0)