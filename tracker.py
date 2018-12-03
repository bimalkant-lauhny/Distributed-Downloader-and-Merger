import sys
import threading
from trackermodule.trackerconfighandler import TrackerConfigHandler
from trackermodule.threadedtrackerserver import ThreadedTrackerServer

if __name__ == "__main__":
    server = None
    try:
        tracker_config = TrackerConfigHandler()
        tracker_config.parseConfig()
        tracker_host = ''
        tracker_port = tracker_config.getTrackerPort()
        tracker_server_address = (tracker_host, tracker_port)
        server = ThreadedTrackerServer(tracker_server_address)
        server.listen()
    
    except Exception as e:
        print("Oops! Error: {}.".format(e))

    finally:
        main_thread = threading.current_thread()
        for t in threading.enumerate():
            if t is main_thread:
                continue
            t.close_connection()
        if server:
            server.stop_server()
    