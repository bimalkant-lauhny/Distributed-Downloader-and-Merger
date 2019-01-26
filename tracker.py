import sys
import threading
from trackermodule.trackerconfighandler import TrackerConfigHandler
from trackermodule.threadedtrackerserver import ThreadedTrackerServer

if __name__ == "__main__":
    server = None
    try:
        tracker_config = TrackerConfigHandler()
        tracker_host = ''
        tracker_port = tracker_config.tracker_port
        tracker_server_address = (tracker_host, tracker_port)
        server = ThreadedTrackerServer(tracker_server_address)
        server.listen()
    
    except Exception as err:
        print("Oops! Error: {}.".format(err))

    finally:
        main_thread = threading.current_thread()
        for t in threading.enumerate():
            if t is main_thread:
                continue
            t.close_connection()
        if server:
            server.stop_server()
    