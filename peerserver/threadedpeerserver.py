"""
Handles connection with clients
"""
import socket
from peerserver.peerclientthread import PeerClientThread


class ThreadedPeerServer:
    """ Multithreaded peer-server that assigns single thread to each peer-client connection """
    def __init__(self, server_address):
        self.server_address = server_address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.server_address)

    def register_with_tracker(self, tracker_server_address, bind_port):
        """ connect to tracker and register ip """
        print("Tracker address: ", tracker_server_address)
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        connection.bind(('', bind_port))
        connection.connect(tracker_server_address)
        print("[+] Connected with Tracker.")
        # register the peer-server
        connection.send("addme".encode())
        print("[+] Sent addme request.")
        # close the connection to tracker
        connection.shutdown(socket.SHUT_RDWR)
        connection.close()
        print("[-] Disconnected with Tracker.")

    def listen(self, temp_dir, threads, proxy):
        """ Listen for client connections """
        print("Server Proxy: ", proxy)
        self.sock.listen(5)
        print("[+] Listening for clients...")
        while True:
            client_conn, client_addr = self.sock.accept()
            print("[+] Client Connected: {}".format(client_addr))
            # client.settimeout(60)
            # assigning a thread to each client connected
            new_client_thread = PeerClientThread(
                client_conn,
                client_addr,
                temp_dir,
                threads,
                proxy
            )
            #new_client_thread.daemon = True
            new_client_thread.start()

    def unregister_with_tracker(self, tracker_server_address, bind_port):
        """ connect to tracker and remove ip """
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        connection.bind(('', bind_port))
        connection.connect(tracker_server_address)
        print("[+] Connected with Tracker.")
        # unregister the peer-server
        connection.send("removeme".encode())
        print("[+] Sent removeme request.")
        # close the connection to tracker
        connection.shutdown(socket.SHUT_RDWR)
        connection.close()
        print("[-] Disconnected with Tracker.")

    def stop_server(self):
        """ stop server execution """
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        print("[-] Stopped Peer Server.")
