import urllib3
import logging
import os.path

logging.getLogger("urllib3").setLevel(logging.WARNING)


url = input("Enter the url to download file: ")
proxy = input("Enter the proxy url (if needed): ")
download_dir = input("Enter the download directory: ")


print (os.path.basename(url))

http = urllib3.PoolManager()
if proxy != "":
	http = urllib3.ProxyManager(proxy)

try:
	resp = http.request("GET", url, retries=5, preload_content=False)
except urllib3.exceptions.NewConnectionError:
	print ("Connection Failed!")

with open(download_dir + os.path.basename(url), "wb") as out:
	while True:
		data = resp.read(1024)
		if not data:
			break
		out.write(data)

resp.release_conn()
