import ConfigParser

from authz.authz import Authz
from authz.htpasswd import HTPasswd

class Config:
	"""Upon construction, it should be checked if files need to be read."""
	cp = None
	authz = None
	htpasswd = None

	def __init__(self, filename=''):
		if not filename:
			import os
			if not os.environ.has_key('SUBMIN_CONF'):
				raise Exception('SUBMIN_CONF environment not found')
			filename = os.environ['SUBMIN_CONF']

		if not self.cp:
			self.cp = ConfigParser.ConfigParser()
			self.cp.read(filename)

		if not self.authz:
			authz_file = ''
			try:
				authz_file = self.get('svn', 'authz_file')
			except ConfigParser.NoSectionError, e:
				raise Exception(
					"Missing config section 'svn' in file %s" % filename)
			except ConfigParser.NoOptionError, e:
				raise Exception(
					"Missing config option 'authz_file' in file %s" % filename)

			self.authz = Authz(authz_file)
		if not self.htpasswd:
			self.htpasswd = HTPasswd(self.get('svn', 'access_file'))

	def get(self, section, variable):
		return self.cp.get(section, variable)
