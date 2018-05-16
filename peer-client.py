import socket 
import ast
import sys
import threading
import json
from calculation import Calculation
from request import Request
from ddm import DistributedDownloaderAndMerger 

class PeerServerThread(threading.Thread):
    ''' establishes and handles the connection to respective peer-server'''
    def __init__(self, url, peer_server_addr, download_range, part_num):
        threading.Thread.__init__(self)
        self.bind_port = 9000 # port used by thread to communicate with respective peer-server 
        self.peer_server_addr = peer_server_addr
        self.url = url
        self.download_range = download_range
        self.part_num = part_num
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
        download_info = {
            "url": self.url, 
            "range-left": self.download_range[0], 
            "range-right": self.download_range[1]}
        download_info = json.dumps(download_info).encode() 
        self.sock.sendall(download_info)
        print("Download info sent: {}".format(download_info))

        filepath = '/home/code_master5/Documents/client-temp/part{}'.format(self.part_num)
        self.receiveFilePart(filepath)
        self.closeConnection()

    # receive file part from server and write at 'filepath'
    def receiveFilePart(self, filepath):
        size = 1024
        print ("Receiving File part...")
        file = open(filepath,'wb')
        chunk = self.sock.recv(size)
        while (chunk):
            file.write(chunk)
            chunk = self.sock.recv(size)
        file.close()
        print ("Done Receiving!")

    def closeConnection(self):
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

    def connectWithPeerServers(self, range_list):
        print("Trying to connect to peer servers...")
        part_num = 0
        for peer_server_addr in self.peer_servers_set:
            download_range = range_list[part_num]
            new_server_thread = PeerServerThread(self.url, peer_server_addr, download_range, part_num)
            part_num += 1
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

        # fetch the list of active servers
        client.fetchPeersList(tracker_server_address, bind_port)

        # if servers doesn't exist, use simple download
        if client.numPeerServers() == 0:
            print ("No peer servers! Using default download...")
            download_object = DistributedDownloaderAndMerger(url)
            download_object.download()

        else:

            print ("Peer Servers found! Distributing download...")

            # get the filesize
            req = Request()
            response = Request.makeRequest(url)
            filesize = int(response.headers['Content-Length'])
            req.closeConnection(response) 
            print ("peer-client filesize: {}".format(filesize))

            # get the download ranges to be assigned to each
            parts = client.numPeerServers()
            range_list = Calculation().get_download_ranges_list(0, filesize-1, parts)

            # connect with each server and send them the download details
            client.connectWithPeerServers(range_list)

            # wait for download to complete at each server

            # servers will send the downloaded part

            # save the downloaded parts

            # after receiving all parts, merge them

            # done 
    except:
        print("Oops!", sys.exc_info()[0], "occured.")
    finally:
        # exit
        sys.exit(0)
