"""
Performs Multithreaded download
"""
import urllib3
import logging
import os
import sys
import shutil
import threading
import pathlib
from utils.filehandler import FileHandler
from utils.request import Request
from utils.calculation import Calculation


class MultithreadedDownloader:
    """Main class providing interface of the software"""
    def __init__(self):
        self.filehandle = FileHandler()
        self.request_handle = Request()
        self.calculate = Calculation()
        self.url = None 
        self.range_left = None
        self.range_right = None
        self.proxy = None 
        self.temp_dir = None 
        self.threads = None 
        self.filepath = None 
        logging.getLogger("urllib3").setLevel(logging.WARNING)

    def range_download_support(self, resp):
        """ returns boolean value indicating support for range downloading """
        try:
            supported = (resp.headers['Accept-Ranges'] == 'bytes')
        except KeyError:
            supported = False

        return supported

    def multithreaded_download(self, ranges_list):
        """ function to perform multithreaded download """
        # downloading each segment
        for f in range(self.threads):
            # calling Downloader.download_range() for each thread
            t = threading.Thread(target=self.request_handle.download_range,
                kwargs={
                'url': self.url,
                'filepath': self.temp_dir + "/temp" + str(f), 
                'range_left': ranges_list[f][0],
                'range_right': ranges_list[f][1],
                'proxy': self.proxy
                })
            t.setDaemon(True)
            t.start()   

        # except main_thread, calling join() for each thread
        # it ensures that merging of parts occur only after each thread has completed downloading
        main_thread = threading.current_thread()
        for t in threading.enumerate():
            if t is main_thread:
                continue
            t.join()    

    def merge_multithreaded_download_parts(self):
        """ function to perform merging of parts performed by multiple threads on single system """
        # merging parts
        with open(self.filepath,'wb') as wfd:
            for f in range(self.threads):
                tempfilepath = self.temp_dir + "/temp" + str(f)
                with open(tempfilepath, "rb") as fd:
                    shutil.copyfileobj(fd, wfd)     
                # delete copied segment
                self.filehandle.delete_file(tempfilepath)

    def download(self, url, range_left, range_right, filepath, 
                 temp_dir, response, threads, proxy=None):
        """ function to perform file download """

        self.url = url
        self.range_right = range_right
        self.range_left = range_left
        self.filepath = filepath        
        self.temp_dir = temp_dir
        self.threads = threads
        self.proxy = proxy

        # if server supports segmented download
        if self.range_download_support(response):
            # get ranges for download for each thread
            ranges_list = self.calculate.get_download_ranges_list(self.range_left, 
                                                            self.range_right,
                                                            self.threads)
            # perform multithreaded download on single system
            self.multithreaded_download(ranges_list)
            # merge multithreaded download parts
            self.merge_multithreaded_download_parts()
        else:   
            print('''Server doesn't support multithreaded downloads!
                Download will be performed using single thread, on master system.''')   
            self.request_handle.download_range(self.url,
                                        self.filepath,
                                        self.range_left, 
                                        self.range_right,
                                        self.proxy)
