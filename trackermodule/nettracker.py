"""
    Tracker Functionality Interface
"""


class NetTracker:
    """ Provides tracker functionality """
    def __init__(self):
        self.peer_servers_set = set()

    def add_peer(self, peer_server):
        """ add a peer server to current list """
        self.peer_servers_set.add(peer_server)

    def remove_peer(self, peer_server):
        """ remove a peer server from current list """
        try:
            self.peer_servers_set.remove(peer_server)
        except KeyError:
            print("{} is not in the list of connected peers!".format(peer_server))

    def get_peer_servers_list(self):
        """ add code for refreshing connected peers """
        return self.peer_servers_set
