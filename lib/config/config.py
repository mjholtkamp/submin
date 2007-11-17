import ConfigParser

class Config:
	def __init__(self):
		self.cp = ConfigParser.ConfigParser()
		self.cp.read("../conf/submin.conf")

	def get(self, section, variable):
		return self.cp.get(section, variable)

