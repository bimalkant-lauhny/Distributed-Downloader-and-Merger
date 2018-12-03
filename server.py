import sys
from utils.calculation import Calculation
from utils.filehandler import FileHandler
from peerserver.peerserverconfighandler import PeerServerConfigHandler
from peerserver.threadedpeerserver import ThreadedPeerServer

if __name__ == '__main__':

    server = None
    filehandle = None

    try:
        peer_server_config = PeerServerConfigHandler()
        peer_server_config.parseConfig()

        temp_dir = peer_server_config.getTempDirPath()
        tracker_host = peer_server_config.getTrackerHost()
        tracker_port = peer_server_config.getTrackerPort()
        tracker_server_address = (tracker_host, tracker_port)
        peer_server_host = ''
        peer_server_port = peer_server_config.getPeerServerPort()
        peer_server_address = (peer_server_host, peer_server_port)

        # port used by peer-server to communicate with tracker-server
        bind_port = peer_server_config.getServerTrackerBindPort() 

        # make sure that temp_dir exists
        filehandle = FileHandler()
        filehandle.createDir(temp_dir)

        server = ThreadedPeerServer(peer_server_address)

        # register the server with tracker
        server.registerWithTracker(tracker_server_address, bind_port)

        proxy = peer_server_config.getProxy() 
        threads = peer_server_config.getNumThreads()
        # listen for download requests from client
        server.listen(temp_dir, threads, proxy)

    except Exception as e:
        print("Oops! Error: {}.".format(e)) 

    finally:

        # stop peer server
        server.stop_server()

        # unregister the server with tracker
        server.unregisterWithTracker(tracker_server_address, bind_port)

        # delete the temporary directory
        filehandle.deleteDir(temp_dir)

        # exit
        sys.exit(0)