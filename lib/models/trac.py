from ConfigParser import NoOptionError, NoSectionError
from config.config import Config
import exceptions
import os

class UnknownTrac(Exception):
	def __init__(self, name):
		Exception.__init__(self, "Could not find trac env '%s'" % name)

class MissingConfig(Exception):
	def __init__(self, msg):
		Exception.__init__(self, '%s' % msg)

class Trac(object):
	def __init__(self, name):
		self.name = name

		config = Config()
		try:
			self.basedir = config.get('trac', 'basedir')
		except (NoOptionError, NoSectionError):
			raise MissingConfig("No 'basedir' in [trac] section")

		tracenv = os.path.join(self.basedir, self.name)
		if not os.path.isdir(tracenv):
			raise UnknownTrac(name)
