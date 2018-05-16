import sys
import ddm

if __name__ == '__main__':
    try:
        # check if download url supplied
        if (len(sys.argv) < 2):
            print ("No Download URL! Exiting ...")
            sys.exit(0)
        url = sys.argv[1]
        download_object = ddm.DistributedDownloaderAndMerger(url)
        download_object.download()
    except KeyboardInterrupt:
        print ('Download Interrupted! Cleaning and Exiting...')
        download_object.final_clean(interrupted=True)
        sys.exit(0)