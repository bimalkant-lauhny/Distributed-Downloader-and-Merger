# Distributed Downloader and Merger (DDM)

Distributed Download Manager is a P2P software that is designed to accomplish the task of downloading large files using a
distributed divide and conquer paradigm. It works on the idea of dividing a file into multiple parts (download ranges) and
assigning the task of downloading a file part to each peer in a network. Every participating peer then downloads the assigned
file part locally and sends it to the local client which requested the download, using a socket connection. The local client
then merges the received parts to get the complete file.

### Architechture

DDM is designed to work on a local network of systems that are also connected to internet. There are basically three types
of systems in a DDM network - tracker, peer server and peer client.
* A tracker server is a system whose main task is to keep information regarding particpating systems. It keeps IP addresses
of all the peer servers in the network, and, supplies this information to peer clients which want to perform distributed
download.
* Peer servers are systems in the network which want to help peer client in performing distributed download. These systems
register themselves with the tracker server and keep listening for connections from clients. When they exit, they send
a `remove` request to tracker, which then removes them from list of current listening servers.
* Peer clients are systems in the network which want to download a file from internet using DDM. They require file URL to
download the file. They ask tracker about currently available peer servers and send each of them some range of file to download.
Peer servers download range of files assigned to them by peer clients and send file parts to respective clients.

### How to run?

You need to install `Python 3` and `pip` to run this project. It is recommended that you should try this project on a network 
of multiple systems with Linux OS installed.

1. Clone the repo in all the systems which plan to run DDM.
2. Open the terminal and go into the directory where DDM is cloned.
3. Type `pip install -r requirements` and wait for packages to install.
4. For each type of system, i.e. tracker, peer server or peer client, you may specify configuration in config files.
5. Choose a system to act as tracker. In tracker system, type `python tracker.py` and press Enter. This will start the 
tracker server.
6. On all other systems that are participating in download process, run peer server by running `python server.py`. This
will start peer server on each system.
7. Now select a system in the network that wants to download file from internet. To download file, say, at sample url
like - https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_10mb.mp4 , run dowload command as
`python client.py https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_10mb.mp4`
8. The process of distributed download starts. If there are no errors, you will find the downloaded file in download directory
specified in config file.


NOTE : DDM is just a fun project that I worked on. There is still room for lot of improvements. So, please feel free to
try DDM, submit issues, feature requests and bug fixes.
