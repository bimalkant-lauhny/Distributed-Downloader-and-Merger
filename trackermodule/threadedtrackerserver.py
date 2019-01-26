"""
    Thread to control connection from peers
"""
import socket
from trackermodule.nettracker import NetTracker
from trackermodule.peerthread import PeerThread


class ThreadedTrackerServer:
    """ Handling threaded connection from peers """
    def __init__(self, tracker_server_address):
        self.tracker_server_address = tracker_server_address
        self.tracker = NetTracker()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.tracker_server_address)

    def listen(self):
        """ listens for client connections """
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
        """ stop tracker server execution """
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        print("[-] Stopped Tracker Server.")
