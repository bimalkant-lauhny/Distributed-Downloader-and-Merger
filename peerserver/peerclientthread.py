import threading
import socket
import multiprocessing
import json
from utils.request import Request
from utils.multithreadeddownloader import MultithreadedDownloader
from utils.calculation import Calculation
from utils.filehandler import FileHandler


class PeerClientThread(threading.Thread):
    ''' class for a thread which handles a peer-client connection'''
    def __init__(self, client_conn, client_addr, temp_dir, threads, proxy):
        threading.Thread.__init__(self)
        self.client_conn = client_conn
        self.client_addr = client_addr 
        self.temp_dir = temp_dir
        self.threads = threads
        self.proxy = proxy

    def run(self):
        size = 1024 
        # receive {"url":"", "range-left":"", "range-right":""} from client
        msg = self.client_conn.recv(size)
        if msg:
            msg = msg.decode()
            print("[+] Received Message: {}".format(msg))
            msg = json.loads(msg)


            # generate a random name for file 
            filename = Calculation().generateRandomString(12)
            filepath = self.temp_dir + filename

            # use request to download
            url = msg['url']
            range_left = msg['range-left']
            range_right = msg['range-right']
            response = Request().makeRequest(url, self.proxy)

            # use Multiprocess to download using multithreading
            print("starting new process to download {}".format(filename))
            p = multiprocessing.Process(
                target=MultithreadedDownloader().download,
                args=(url, range_left, range_right, filepath, self.temp_dir, 
                    response, self.threads, self.proxy, )) 
            p.start()
            p.join()
            print ('Out of process for file {}'.format(filename))

            # send the downloaded file part to peer-client 
            self.sendFilePart(filepath)

            # let peer-client know that file sending is done
            self.client_conn.shutdown(socket.SHUT_RDWR)

            # close connection with peer-client
            self.client_conn.close()
            print("[-] Client Disconnected: {}".format(self.client_addr))

            # delete temp file
            FileHandler().deleteFile(filepath)
            print("[-] Temp File Deleted.")

    # function for sending file at 'filepath' through socket to client
    def sendFilePart(self, filepath):
        file = open(filepath,'rb')
        chunk = file.read(1024)
        print('Sending...')
        while (chunk):
            self.client_conn.send(chunk)
            chunk = file.read(1024)
        file.close()
        print ("Done Sending File!")