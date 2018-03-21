import urllib3
import logging
import os
import sys
import shutil
import argparse
import threading

parser = argparse.ArgumentParser()
parser.add_argument("--url", 
					help="Enter the URL of the file (Required)")
parser.add_argument("--proxy", 
					help='''Enter the proxy if required, 
					default = no proxy''')
parser.add_argument("--dir", 
					help='''Enter the directory to store the downloaded file, 
					default = ~/Downloads/''')
parser.add_argument("--timeout", 
					help='''Enter the request timeout in seconds,
					default = 5.0''', 
					type=float)
parser.add_argument("--retries", 
					help='''Enter the number of retries,
					default = 5''',
					type=int)

parser.add_argument("--threads", 
					help='''Enter the number of threads,
					default = 2''',
					type=int)
args = parser.parse_args()

if not args.url:
	print("You didn't supply the download URL! See --help or -h for details.")	
	sys.exit()

if not args.dir:
	args.dir = "~/Downloads/"
	print("No --dir supplied! Using default path ~/Downloads/")

if not args.timeout:
	args.timeout = 5.0	

if not args.retries:
	args.retries = 5

if not args.threads:
	args.threads = 2

logging.getLogger("urllib3").setLevel(logging.WARNING)

http = urllib3.PoolManager()
if args.proxy:
	http = urllib3.ProxyManager(args.proxy)


def make_request(url, retries, timeout, headers=None):

	try:
		resp = http.request("GET", 
			url.replace("https", "http"), 
			retries=retries, 
			timeout=timeout,
			preload_content=False,
			headers=headers)
	except urllib3.exceptions.NewConnectionError:
		print ("Connection Failed!")
	except urllib3.exceptions.SSLError:
		print ("SSL Error!")

	return resp


def seg_handler(url, filepath, range_left, range_right, retries, timeout):

	resp = make_request(url, retries, timeout, {'Range': 'bytes=%d-%d' % (range_left, range_right)})
	
	chunk_size = 1024 * 256 #256KB

	with open(filepath, "wb") as fp:

		downloaded = 0 #in KBs

		while True:
			data = resp.read(chunk_size)

			if not data:
				print("\nDownload Finished.")
				break

			fp.write(data)
			downloaded += sys.getsizeof(data) 
			print ("\r{0:.2f} MB".format(downloaded), end="")

	resp.release_conn()


#extracting filename from URL
filename = os.path.basename(args.url).replace("%20", "_")

# getting complete filepath
filepath = args.dir + "/" + filename

#making a dummy request to get header information
resp = make_request(args.url, args.retries, args.timeout)

# size of file to be downloaded in bytes
filesize = int(resp.headers['Content-Length'])

# Checking multithreaded download support
if resp.headers['Accept-Ranges'] == "bytes":

	# no of bytes per thread
	size_per_thread = filesize//args.threads

	# stores size to be downloaded by each thread
	sizes_list = [size_per_thread] * args.threads
	# remaining size not assigned to any thread 
	rem = filesize % args.threads	
	# loop to equally assign sizes to download, to each thread
	index = 0
	while rem != 0:
		sizes_list[index] += 1
		rem -= 1
		index += 1

	sizes_list.insert(0, 0)

	index = 2 
	while index < len(sizes_list):
		sizes_list[index] += sizes_list[index - 1]
		index += 1

	# list storing tuples of byte-ranges
	ranges_list = []
	index = 1
	while index < len(sizes_list):
		ranges_list.append((sizes_list[index - 1],sizes_list[index] - 1))
		index += 1

	# downloading each segment
	for f in range(args.threads):
		# calling seg_handler() for each thread
		t = threading.Thread(target=seg_handler,
               				kwargs={
               					'url': args.url, 
               					'filepath': args.dir + "/temp" + str(f), 
               					'range_left': ranges_list[f][0],
               					'range_right': ranges_list[f][1],
               					'retries': args.retries,
               					'timeout': args.timeout
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

	# merging parts
	with open(filepath,'wb') as wfd:
		for f in range(args.threads):
			with open(args.dir + "/temp" + str(f), "rb") as fd:
				shutil.copyfileobj(fd, wfd)		
			# delete copied segment
			os.unlink(args.dir + "/temp" + str(f))

else:
	print('''Server doesn't support multithreaded downloads!
			Download will be performed using single thread.''')	
	seg_handler(args.url, filepath, 0, filesize-1, args.retries, args.timeout)
