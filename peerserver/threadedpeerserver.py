import socket
from peerserver.peerclientthread import PeerClientThread

class ThreadedPeerServer:
    ''' Multithreaded peer-server that assigns single thread to each peer-client connection'''
    def __init__(self, server_address):
        self.server_address = server_address 
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.server_address)

    def registerWithTracker(self, tracker_server_address, bind_port):
        # connect to tracker
        print ("Tracker address: ", tracker_server_address)
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

    def listen(self, temp_dir, threads, proxy):
        print("Server Proxy: ", proxy)
        self.sock.listen(5)
        print("[+] Listening for clients...")
        while True:
            client_conn, client_addr = self.sock.accept()
            print("[+] Client Connected: {}".format(client_addr))
            #client.settimeout(60)
            # assigning a thread to each client connected
            new_client_thread = PeerClientThread(client_conn, client_addr, 
                                                temp_dir, threads, proxy)
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