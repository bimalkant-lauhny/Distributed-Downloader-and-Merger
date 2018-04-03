import os
import shutil

class FileHandler:
	''' Class for file and directory handling operations'''

	# function for clean deletion of a file at filepath
	def delete_file(self, filepath):
		try:
			os.remove(filepath)
		except OSError as err:
			print("OS error: {0}".format(err))

	# create directory at dirpath
	def create_dir(self, dirpath):
		try:
			os.mkdir(dirpath)
		except FileExistsError:
			print("Directory already exists!")	

	# recursive deletion of a directory at dirpath
	def delete_dir(self, dirpath):
		try:
			shutil.rmtree(dirpath)
		except OSError as err:
			print("OS error: {0}".format(err))