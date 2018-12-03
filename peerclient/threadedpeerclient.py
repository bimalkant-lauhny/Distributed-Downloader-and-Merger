import ast
import socket
from peerclient.peerserverthread import PeerServerThread


class ThreadedPeerClient:

    def __init__(self, url):
        self.url = url
        self.peer_servers_set = None	

    def fetchPeersList(self, tracker_server_address, client_tracker_bind_port):
        # connect to tracker
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', client_tracker_bind_port))
        s.connect(tracker_server_address)
        print("[+] Connected with Tracker.")
        # ask the tracker for peers list
        s.send("sendpeerslist".encode())
        print("[+] Sent sendpeerslist request.")
        # receive peers list as a set of address tuples
        msg = s.recv(1024)
        msg = msg.decode()
        if msg == "None":
            self.peer_servers_set = set() 
        else:
            self.peer_servers_set = ast.literal_eval(msg)
        print("[+] Received Peers List: {}".format(self.peer_servers_set))
        # close the connection to tracker       
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        print("[-] Disconnected with Tracker.")

    def numPeerServers(self):
        return len(self.peer_servers_set)

    def connectWithPeerServers(self, range_list, temp_dir, client_server_bind_port):
        print("Trying to connect to peer servers...")
        part_num = 0
        for peer_server_addr in self.peer_servers_set:
            download_range = range_list[part_num]
            new_server_thread = PeerServerThread(self.url, 
                                    peer_server_addr, 
                                    download_range, 
                                    part_num,
                                    temp_dir,
                                    client_server_bind_port)
            part_num += 1
            #new_server_thread.daemon = True
            new_server_thread.start()
