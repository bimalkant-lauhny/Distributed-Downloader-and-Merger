"""
 Extended thread class to control connection from peers
"""
import threading
import socket


class PeerThread(threading.Thread):
    """ Controlling threaded connection from peers """
    def __init__(self, tracker, peer_conn, peer_addr):
        threading.Thread.__init__(self)
        self.tracker = tracker
        self.peer_conn = peer_conn
        self.peer_addr = peer_addr

    def run(self):
        """ Extends run function that runs thread """
        size = 1024
        msg = self.peer_conn.recv(size)
        if msg:
            msg = msg.decode()
            print("[+] Received Message: {}".format(msg))
            if msg == "addme":
                # peer-server wants to act as server
                self.tracker.add_peer(self.peer_addr)
                print("Updated trackers list: {}".format(self.tracker.getPeerServersList()))
                self.close_connection()
                print("[-] Peer Server Added to List: {}".format(self.peer_addr))
            elif msg == "sendpeerslist":
                # peer-client needs peer-servers list to distribute the download
                response = self.tracker.get_peer_servers_list()
                if response == set():
                    response = "None"
                response = str(response).encode()
                self.peer_conn.sendall(response)
                print("[+] Sent Peer Servers List to: {}".format(self.peer_addr))
                self.close_connection()
            elif msg == "removeme":
                # peer-server wants to leave the network
                self.tracker.remove_peer(self.peer_addr)
                print("Updated trackers list: {}".format(self.tracker.get_peer_servers_ilist()))
                self.close_connection()
                print("[-] Peer Server removed from List: {}".format(self.peer_addr))

    def close_connection(self):
        """ closing connection with peer """
        self.peer_conn.shutdown(socket.SHUT_RDWR)
        self.peer_conn.close()
        print("[-] Closed Connection with {}.".format(self.peer_addr))
