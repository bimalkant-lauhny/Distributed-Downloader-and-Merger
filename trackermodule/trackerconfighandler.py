import configparser

class TrackerConfigHandler:

	""" cofig details from tracker-config.ini"""

	def __init__(self):
		self.tracker_port = None

	def parseConfig(self):
		config = configparser.ConfigParser()
		config.read('configfiles/tracker-config.ini')

		try:
			self.tracker_port = int(config['TRACKER']['TRACKER_PORT'])
		except:
			print("No tracker port provided")

	def getTrackerPort(self):
		return self.tracker_port	

