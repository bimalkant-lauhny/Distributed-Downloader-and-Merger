import socket 
import ast
import sys
import os
import shutil
import threading
import json
from calculation import Calculation
from request import Request
from filehandler import FileHandler
from peerclientconfighandler import PeerClientConfigHandler
from ddm import DistributedDownloaderAndMerger 

class PeerServerThread(threading.Thread):
    ''' establishes and handles the connection to respective peer-server'''
    def __init__(self, url, peer_server_addr, download_range, part_num, temp_dir):

        threading.Thread.__init__(self)
        self.bind_port = 9000 # port used by thread to communicate with respective peer-server 
        self.peer_server_addr = peer_server_addr
        self.url = url
        self.temp_dir = temp_dir
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

        filepath = self.temp_dir + '/part{}'.format(self.part_num)
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

    def connectWithPeerServers(self, range_list, temp_dir):
        print("Trying to connect to peer servers...")
        part_num = 0
        for peer_server_addr in self.peer_servers_set:
            download_range = range_list[part_num]
            new_server_thread = PeerServerThread(self.url, 
                                    peer_server_addr, 
                                    download_range, 
                                    part_num,
                                    temp_dir)
            part_num += 1
            #new_server_thread.daemon = True
            new_server_thread.start()



if __name__ == '__main__':
    
    try:
        peerClientConfig = PeerClientConfigHandler()
        peerClientConfig.parseConfig()    

        tracker_host = peerClientConfig.getTrackerHost() 
        tracker_port = peerClientConfig.getTrackerPort() 
        tracker_server_address = (tracker_host, tracker_port)
        temp_dir = peerClientConfig.getTempDirPath()

        filehandle = FileHandler()
        filehandle.create_dir(temp_dir)

        # check if download url supplied
        if (len(sys.argv) < 2):
            print ("No Download URL! Exiting ...")
            sys.exit(0)
        url = sys.argv[1]
        client = ThreadedPeerClient(url)
        # port used by peer-client to communicate with tracker
        bind_port = peerClientConfig.getClientTrackerBindPort() 

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
            response = req.makeRequest(url, proxy=peerClientConfig.getProxy())
            filesize = int(response.headers['Content-Length'])
            req.closeConnection(response) 
            print ("peer-client filesize: {}".format(filesize))

            # get the download ranges to be assigned to each
            parts = client.numPeerServers()
            range_list = Calculation().get_download_ranges_list(0, filesize-1, parts)

            # connect with each server and send them the download details
            client.connectWithPeerServers(range_list, temp_dir)

            # wait for download to complete at each server
            # except main_thread, calling join() for each thread
            # it ensures that merging of parts occur only after each thread has completed downloading
            # print ("Threads: ", len(threading.enumerate()))
            main_thread = threading.current_thread()
            for t in threading.enumerate():
                if t is main_thread:
                    continue
                t.join()
                
            # servers will send the downloaded part

            # save the downloaded parts

            # after receiving all parts, merge them

            # merging parts
            filename = os.path.basename(url.replace("%20", "_"))
            filepath =  temp_dir + filename 
            with open(filepath,'wb') as wfd:
                for f in range(parts):
                    tempfilepath = temp_dir + "/part" + str(f)
                    with open(tempfilepath, "rb") as fd:
                        shutil.copyfileobj(fd, wfd)     
                    # delete copied segment
                    filehandle.delete_file(tempfilepath)
            # done 
    except:
        print("Oops!", sys.exc_info(), "occured.")
    finally:
        # exit
        sys.exit(0)
