import urllib3
import logging
import os.path
import sys

logging.getLogger("urllib3").setLevel(logging.WARNING)


url = input("Enter the url to download file: ")
proxy = input("Enter the proxy url (if needed): ")
download_dir = input("Enter the download directory: ")

http = urllib3.PoolManager()
if proxy != "":
	http = urllib3.ProxyManager(proxy)

def make_request(url):
	return http.request("GET", 
						url.replace("https", "http"), 
						retries=5, 
						preload_content=False)

try:
	resp = make_request(url)	
except urllib3.exceptions.NewConnectionError:
	print ("Connection Failed!")
except urllib3.exceptions.SSLError:
	print ("SSL Error!")

filename = os.path.basename(url).replace("%20", "_")
print(filename)

chunk_size = 1024 * 256 #256KB
with open(download_dir + filename, "wb") as out:
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
