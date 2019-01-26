import sys
import os
import shutil
import threading
from utils.calculation import Calculation
from utils.request import Request
from utils.filehandler import FileHandler
from utils.multithreadeddownloader import MultithreadedDownloader 
from peerclient.threadedpeerclient import ThreadedPeerClient 
from peerclient.peerclientconfighandler import PeerClientConfigHandler


if __name__ == '__main__':
    
    try:
        peer_client_config = PeerClientConfigHandler()

        tracker_host = peer_client_config.tracker_host
        tracker_port = peer_client_config.tracker_port
        tracker_server_address = (tracker_host, tracker_port)

        temp_dir = peer_client_config.temp_dir
        download_dir = peer_client_config.download_dir
        proxy = peer_client_config.proxy
        threads = peer_client_config.proxy

        try:
            filehandle = FileHandler()
            # make sure that the temp_dir and download_dir exist
            filehandle.createDir(os.path.abspath(temp_dir))
            filehandle.createDir(os.path.abspath(download_dir))
        except Exception as e:
            print("Oops! Error: {}.".format(e))

        # check if download url supplied
        if (len(sys.argv) < 2):
            print ("No Download URL! Exiting ...")
            sys.exit(0)
        url = sys.argv[1]
        client = ThreadedPeerClient(url)
        # port used by peer-client to communicate with tracker
        client_tracker_bind_port = peer_client_config.client_tracker_bind_port

        # fetch the list of active servers
        client.fetch_peers_list(tracker_server_address, client_tracker_bind_port)

        # make request to url to get information about file
        req = Request()
        response = req.makeRequest(url, proxy=proxy)
        req.closeConnection(response) 

        # get the filesize
        filesize = int(response.headers['Content-Length'])
        filename = os.path.basename(url.replace("%20", "_"))
        filepath =  download_dir + '/' + filename 

        # if range-download is not supported, use simple download
        if response.headers['Accept-Ranges'] != 'bytes':
            print ("URL doesn't support range download! Using default download...")
            MultithreadedDownloader().download(url, 0, filesize-1, filepath, 
                                            temp_dir, response, threads, proxy)
        # if servers doesn't exist, use simple download
        elif client.num_peer_servers() == 0:
            print ("No peer servers! Using default download...")
            MultithreadedDownloader().download(url, 0, filesize-1, filepath, 
                                            temp_dir, response, threads, proxy)
        else:
            print ("Peer Servers found! Distributing download...")
            print ("peer-client filesize: {}".format(filesize))

            # get the download ranges to be assigned to each
            parts = client.num_peer_servers()
            range_list = Calculation().getDownloadRangesList(0, filesize-1, parts)

            # connect with each server and send them the download details
            client_server_bind_port = peer_client_config.client_server_bind_port
            client.connect_with_peer_servers(range_list, temp_dir, client_server_bind_port)

            # wait for download to complete at each server
            # except main_thread, calling join() for each thread
            # it ensures that merging of parts occur only after each thread has -
            # received downloaded part from respective server 
            main_thread = threading.current_thread()
            for t in threading.enumerate():
                if t is main_thread:
                    continue
                t.join()
                
            # after receiving all parts, merge them
            with open(filepath,'wb') as wfd:
                for f in range(parts):
                    tempfilepath = temp_dir + "/part" + str(f)
                    with open(tempfilepath, "rb") as fd:
                        shutil.copyfileobj(fd, wfd)     
                    # delete copied segment
                    filehandle.deleteFile(tempfilepath)
    except ConnectionError:
        print ("Connection Error! Falling back to download at client...")
    except Exception as e:
        print("Oops! Error: {}.".format(e))
        # delete the file if error occured
        filehandle.deleteFile(filepath)
    finally:
        # delete temporary directory
        filehandle.deleteDir(temp_dir)
        # exit
        sys.exit(0)
