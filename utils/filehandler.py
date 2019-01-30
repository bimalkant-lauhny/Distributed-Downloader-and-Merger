"""
 File handling
"""
import os
import shutil


class FileHandler:
    """ Class for file and directory handling operations """

    def delete_file(self, filepath):
        """ function for clean deletion of a file at filepath """
        try:
            os.remove(filepath)
        except Exception as err:
            print("Error: {0}".format(err))

    def create_dir(self, dirpath):
        """ create directory at dirpath """
        try:
            os.makedirs(dirpath)
        except Exception as err:
            print("Error: {0}".format(err))

    def delete_dir(self, dirpath):
        """ recursive deletion of a directory at dirpath """
        try:
            shutil.rmtree(dirpath)
        except Exception as err:
            print("Error: {0}".format(err))
