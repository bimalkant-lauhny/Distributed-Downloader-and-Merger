"""
    Reads and stores config parameters from tracker config file
"""
import configparser


class TrackerConfigHandler:
    """ config details from tracker-config.ini"""
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('configfiles/tracker-config.ini')

        try:
            self.tracker_port = int(config['TRACKER']['TRACKER_PORT'])
        except Exception as err:
            print("Error: {}".format(err))
            self.tracker_port = None
