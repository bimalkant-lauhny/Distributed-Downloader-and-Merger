import sys
import ddm

def main(download_object):
	download_object.download()

if __name__ == '__main__':
	try:
		download_object = ddm.DistributedDownloaderAndMerger()
		main(download_object)
	except KeyboardInterrupt:
		print ('Download Interrupted! Cleaning and Exiting...')
		download_object.final_clean(interrupted=True)
		sys.exit(0)