"""
Handles config parameters from server config file
"""
import configparser
import pathlib
import os


class PeerServerConfigHandler:
    """Class for PeerServerConfigHandler"""
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('configfiles/peer-server-config.ini')

        try:
            self.peer_server_port = int(config['SERVER']['PEER_SERVER_PORT'])
        except KeyError:
            print("No peer_server_port provided")
            self.peer_server_port = 6000

        try:
            self.tracker_port = int(config['SERVER']['TRACKER_PORT'])
        except KeyError:
            print("No tracker_port provided ")
            self.tracker_port = 5000

        try:
            self.tracker_host = config['SERVER']['TRACKER_HOST']
        except KeyError:
            print("No tracker_host provided ")
            self.tracker_host = ''

        try:
            self.server_tracker_bind_port = int(config['SERVER']['SERVER_TRACKER_BIND_PORT'])
        except KeyError:
            print("No server_tracker_bind_port provided ")
            self.server_tracker_bind_port = 6000

        try:
            self.temp_dir = os.path.abspath(config['SERVER']['TEMP_DIR'] + '/')
        except KeyError:
            print("No temp_dir provided ")
            self.temp_dir = os.path.abspath(str(pathlib.Path.home()) + "/Downloads/server-temp/")

        try:
            self.proxy = config['SERVER']['PROXY']
        except KeyError:
            print("No proxy provided!")
            self.proxy = None

        try:
            self.threads = int(config['SERVER']['THREADS'])
        except KeyError:
            print("Number of download threads are not specified! Setting default to 4 threads.")
            self.threads = 4
