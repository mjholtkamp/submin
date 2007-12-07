import ConfigParser

from authz.authz import Authz
from authz.htpasswd import HTPasswd

class Config:
	"""Upon construction, it should be checked if files need to be read."""
	cp = None
	authz = None
	htpasswd = None

	def __init__(self, filename='../conf/submin.conf'):
		if not self.cp:
			self.cp = ConfigParser.ConfigParser()
			self.cp.read(filename)

		if not self.authz:
			self.authz = Authz(self.get('svn', 'authz_file'))
		if not self.htpasswd:
			self.htpasswd = HTPasswd(self.get('svn', 'access_file'))

	def get(self, section, variable):
		return self.cp.get(section, variable)
