import ConfigParser

class Config:
	def __init__(self):
		self.cp = ConfigParser.ConfigParser()
		self.cp.read("../conf/submerge.conf")

	def get(self, section, variable):
		return self.cp.get(section, variable)

