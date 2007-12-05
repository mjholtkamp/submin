import ConfigParser

from authz.authz import Authz
from authz.htpasswd import HTPasswd

class Config:
	def __init__(self):
		self.cp = ConfigParser.ConfigParser()
		self.cp.read("../conf/submin.conf")

		self.authz = Authz(self.get('svn', 'authz_file'))
		self.htpasswd = HTPasswd(self.get('svn', 'access_file'))

	def get(self, section, variable):
		return self.cp.get(section, variable)

