import configparser


class TrackerConfigHandler:
	def __init__(self):
		self.tracker_port = None

	def parseConfig(self):
		config = configparser.ConfigParser()
		config.read('tracker-config.ini')


		try:
			self.tracker_port = config['TRACKER']['TRACKER_PORT']
		except:
			print("No tracker port provided")

	def get_tracker_port(self):
		return self.tracker_port	

