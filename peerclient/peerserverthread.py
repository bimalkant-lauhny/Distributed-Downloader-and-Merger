import socket
import threading
import json


class PeerServerThread(threading.Thread):
    ''' establishes and handles the connection to respective peer-server'''
    def __init__(self, url, peer_server_addr, download_range, part_num, 
                 temp_dir, client_server_bind_port):

        threading.Thread.__init__(self)
        # port used by thread to communicate with respective peer-server 
        self.client_server_bind_port = client_server_bind_port 
        self.peer_server_addr = peer_server_addr
        self.url = url
        self.temp_dir = temp_dir
        self.download_range = download_range
        self.part_num = part_num
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.client_server_bind_port))

    def run(self):
        size = 1024
        # connect to peer-server 
        print("[+] Trying to connect to {}".format(self.peer_server_addr))
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