import sys
from utils.calculation import Calculation
from utils.filehandler import FileHandler
from peerserver.peerserverconfighandler import PeerServerConfigHandler
from peerserver.threadedpeerserver import ThreadedPeerServer

if __name__ == '__main__':

    server = None
    filehandle = None
    peer_server_config = PeerServerConfigHandler()

    temp_dir = peer_server_config.temp_dir
    tracker_host = peer_server_config.tracker_host
    tracker_port = peer_server_config.tracker_port
    tracker_server_address = (tracker_host, tracker_port)
    peer_server_host = ''
    peer_server_port = peer_server_config.peer_server_port
    peer_server_address = (peer_server_host, peer_server_port)

    # port used by peer-server to communicate with tracker-server
    bind_port = peer_server_config.server_tracker_bind_port

    filehandle = FileHandler()
    filehandle.createDir(temp_dir)
    try:

        server = ThreadedPeerServer(peer_server_address)
        # register the server with tracker
        server.register_with_tracker(tracker_server_address, bind_port)

        proxy = peer_server_config.proxy
        threads = peer_server_config.threads
        # listen for download requests from client
        server.listen(temp_dir, threads, proxy)

    except Exception as e:
        print("Oops! Error: {}.".format(e)) 

    finally:

        # stop peer server
        if server: 
            server.stop_server()
            # unregister the server with tracker
            server.unregister_with_tracker(tracker_server_address, bind_port)

        # delete the temporary directory
        filehandle.deleteDir(temp_dir)

        # exit
        sys.exit(0)
