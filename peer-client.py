import socket 
import ast
import sys
import threading
import json

class PeerServerThread(threading.Thread):
    ''' establishes and handles the connection to respective peer-server'''
    def __init__(self, url, peer_server_addr):
        threading.Thread.__init__(self)
        self.bind_port = 9000 # port used by thread to communicate with respective peer-server 
        self.peer_server_addr = peer_server_addr
        self.url = url
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.bind_port))

    def run(self):
        size = 1024
        # connect to peer-server 
        print("[+] Trying to connect to {}".format(self.peer_server_addr))
        input("Connect to {}:".format(self.peer_server_addr))
        self.sock.connect(self.peer_server_addr)
        print("[+] Connected with Server at {}".format(self.peer_server_addr))
        # send {"url":"", "range-left":"", "range-right":""} to peer-server 
        download_info = {"url": self.url, "range-left": 1234, "range-right": 4321}
        download_info = json.dumps(download_info).encode() 
        self.sock.sendall(download_info)
        print("Download info sent: {}".format(download_info))

        msg = self.sock.recv(size)
        data = b''
        while msg:
            data += msg
            msg = self.sock.recv(size)
        data = data.decode()
        print("[+] Received Message: {}".format(data))
        self.close_connection()

    def close_connection(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        print("[-] Peer-Server Disconnected: {}".format(self.peer_server_addr))

class ThreadedPeerClient:

    def __init__(self, url):
        self.url = url
        self.peer_servers_set = None	

    def fetchPeersList(self, tracker_server_address, bind_port):
        # connect to tracker
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', bind_port))
        s.connect(tracker_server_address)
        print("[+] Connected with Tracker.")
        # ask the tracker for peers list
        s.send("sendpeerslist".encode())
        print("[+] Sent sendpeerslist request.")
        # receive peers list as a set of address tuples
        msg = s.recv(1024)
        msg = msg.decode()
        self.peer_servers_set = ast.literal_eval(msg)
        print("[+] Received Peers List: {}".format(self.peer_servers_set))
        # close the connection to tracker       
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        print("[-] Disconnected with Tracker.")

    def peerServersExist(self):
        if len(self.peer_servers_set) > 0:
            return True
        return False

    def connectWithPeerServers(self):
        print("Trying to connect to peer servers...")
        for peer_server_addr in self.peer_servers_set:
            new_server_thread = PeerServerThread(self.url, peer_server_addr)
            #new_server_thread.daemon = True
            new_server_thread.start()

if __name__ == '__main__':
    try:
        # check if download url supplied
        if (len(sys.argv) < 2):
            print ("No Download URL! Exiting ...")
            sys.exit(0)
        url = sys.argv[1]
        tracker_host = ''
        tracker_port = 5000
        tracker_server_address = (tracker_host, tracker_port)
        client = ThreadedPeerClient(url)
        bind_port = 8000 # port used by peer-client to communicate with tracker
        client.fetchPeersList(tracker_server_address, bind_port)
        client.connectWithPeerServers()
    except:
        print("Oops!", sys.exc_info()[0], "occured.")
    finally:
        # exit
        sys.exit(0)
