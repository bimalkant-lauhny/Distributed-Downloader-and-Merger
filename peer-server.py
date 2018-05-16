import sys
import socket
import threading
import json
from downloader import Downloader 

class PeerClientThread(threading.Thread):
    ''' class for a thread which handles a peer-client connection'''
    def __init__(self, client_conn, client_addr):
        threading.Thread.__init__(self)
        self.client_conn = client_conn
        self.client_addr = client_addr 

    def run(self):
        size = 1024 
        # receive {"url":"", "range-left":"", "range-right":""} from client
        msg = self.client_conn.recv(size)
        if msg:
            msg = msg.decode()
            print("[+] Received Message: {}".format(msg))
            msg = json.loads(msg)

            # TODO: use Multiprocess to download using multithreading

            # TODO: use tracker-config get filepath, proxy, timeouts, retries etc 

            # use request to download
            filepath = '/home/code_master5/Documents/temp/file-1' 

            Downloader().download(msg['url'], 
                proxy=None, 
                filepath=filepath, 
                msg['range_left'], 
                msg['range_right'])

            # send the downloaded file part to peer-client 
            self.sendFile(filepath)

            # let peer-client know that file sending is done
            self.client_conn.shutdown(socket.SHUT_RDWR)

            # close connection with peer-client
            self.client_conn.close()
            print("[-] Client Disconnected: {}".format(self.client_addr))

    # function for sending file at 'filepath' through socket to client
    def sendFile(self, filepath):
        file = open(filepath,'rb')
        chunk = file.read(1024)
        print('Sending...')
        while (chunk):
            client_conn.send(chunk)
            chunk = file.read(1024)
        file.close()
        print "Done Sending File!"

class ThreadedPeerServer:
    ''' Multithreaded peer-server that assigns single thread to each peer-client connection'''
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
            client_conn, client_addr = self.sock.accept()
            print("[+] Client Connected: {}".format(client_addr))
            #client.settimeout(60)
            # assigning a thread to each client connected
            new_client_thread = PeerClientThread(client_conn, client_addr)
            #new_client_thread.daemon = True
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

    def stop_server(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        print("[-] Stopped Peer Server.")

if __name__ == '__main__':
    tracker_host = ''
    tracker_port = 5000
    tracker_server_address = (tracker_host, tracker_port)
    peer_server_host = ''
    peer_server_port = 6000
    peer_server_address = (peer_server_host, peer_server_port)
    bind_port = 6000 # port used by peer-server to communicate with tracker-server
    server = None

    try:
        server = ThreadedPeerServer(peer_server_address)

        # register the server with tracker
        server.registerWithTracker(tracker_server_address, bind_port)

        # listen for download requests from client
        server.listen()

    except:
        print("Oops!", sys.exc_info()[0], "occured.") 

    finally:
        server.stop_server()
        server.unregisterWithTracker(tracker_server_address, bind_port)
        # exit
        sys.exit(0)