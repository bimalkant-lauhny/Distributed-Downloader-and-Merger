import urllib3
import logging
import os.path
import sys
import argparse

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

args = parser.parse_args()

if not args.url:
	print("You didn't supply the download URL! See --help or -h for details.")	

if not args.dir:
	args.dir = "~/Downloads/"
	print("No --dir supplied! Using default path ~/Downloads/")

if not args.timeout:
	args.timeout = 5.0	

if not args.retries:
	args.retries = 5

logging.getLogger("urllib3").setLevel(logging.WARNING)

http = urllib3.PoolManager()
if args.proxy:
	http = urllib3.ProxyManager(args.proxy)

def make_request(url):
	#makes GET request to fetch file
	return http.request("GET", 
						args.url.replace("https", "http"), 
						retries=args.retries, 
						timeout=args.timeout,
						preload_content=False)

try:
	resp = make_request(args.url)	
	print("Response: ", resp.headers['Content-Type'])
except urllib3.exceptions.NewConnectionError:
	print ("Connection Failed!")
except urllib3.exceptions.SSLError:
	print ("SSL Error!")

filename = os.path.basename(args.url).replace("%20", "_")
print(filename)

chunk_size = 1024 * 256 #256KB
with open(args.dir + filename, "wb") as out:
	downloaded = 0 #in KBs
	while True:
		data = resp.read(chunk_size)
		if not data:
			print("\nDownload Finished.")
			break
		out.write(data)
		downloaded += sys.getsizeof(data) 
		print ("\r{0:.2f} MB".format(downloaded/(1024 * 1024)), end="")

resp.release_conn()
