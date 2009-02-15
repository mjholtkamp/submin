import ConfigParser
import os

from authz.authz import Authz
from authz.htpasswd import HTPasswd

from path.path import Path

class CouldNotReadConfig(Exception):
	def __init__(self, msg):
		Exception.__init__(self, msg)

class ConfigData:
	"""Upon construction, it should be checked if files need to be read."""
	cp = None
	authz = None
	htpasswd = None

	def __init__(self, filename=''):
		self.ctimes = {}
		self.ctimes["config"] = 0
		self.ctimes["authz"] = 0
		self.ctimes["userprop"] = 0
		self.ctimes["htpasswd"] = 0
		self.version = 1
		self.use_env = False
		self.filename = filename
		if not filename:
			self.use_env = True

		self.reinit()

	def _ctime(self, filename):
		try:
			s = os.stat(filename)
			return s.st_ctime
		except OSError:
			return 0

	def reinit(self):
		if os.environ.has_key('SUBMIN_ENV'):
			self.version = 2
			self.base_path = Path(os.environ['SUBMIN_ENV'])
			self.filename = str(self.base_path + 'conf' + 'submin.ini')
			self.use_env = False
			self.template_path = self.base_path + 'static' + 'templates'

		filename = self.filename
		if self.use_env:
			if not os.environ.has_key('SUBMIN_CONF'):
				raise Exception('SUBMIN_CONF environment not found')
			self.filename = os.environ['SUBMIN_CONF']
			if filename != self.filename:
				self.ctimes["config"] = 0
				self.ctimes["authz"] = 0
				self.ctimes["userprop"] = 0
				self.ctimes["htpasswd"] = 0
				filename = self.filename
		
		try:
			conf_stat = os.stat(self.filename)
		except OSError, e:
			raise CouldNotReadConfig(str(e))

		conf_ctime = conf_stat.st_ctime 
		if not self.cp or conf_ctime > self.ctimes["config"]:
			self.cp = ConfigParser.ConfigParser()
			files = self.cp.read(self.filename)
			if len(files) == 0:
				raise CouldNotReadConfig('File is empty?')

			self.ctimes["config"] = conf_ctime

		# authz/userprop preparation
		authz_file = ''
		userprop_file = ''
		try:
			authz_file = str(self.getpath('svn', 'authz_file'))
		except ConfigParser.NoSectionError, e:
			raise Exception(
				"Missing config section 'svn' in file %s" % filename)
		except ConfigParser.NoOptionError, e:
			raise Exception(
				"Missing config option 'authz_file' in file %s" % filename)

		try:
			userprop_file = str(self.getpath('svn', 'userprop_file'))
		except ConfigParser.NoSectionError, e:
			raise Exception(
				"Missing config section 'svn' in file %s" % filename)
		except ConfigParser.NoOptionError, e:
			raise Exception(
				"Missing config option 'userprop_file' in file %s" % \
						filename)

		authz_ctime = self._ctime(authz_file)
		refresh_authz = authz_ctime > self.ctimes["authz"]

		userprop_ctime = self._ctime(userprop_file)
		refresh_userprop = userprop_ctime > self.ctimes["userprop"]

		if not self.authz or refresh_authz or refresh_userprop:
			self.authz = Authz(authz_file, userprop_file)
			self.ctimes["authz"] = authz_ctime
			self.ctimes["userprop"] = userprop_ctime

		htpasswd_file = str(self.getpath('svn', 'access_file'))
		htpasswd_ctime = self._ctime(htpasswd_file)
		if not self.htpasswd or htpasswd_ctime > self.ctimes["htpasswd"]:
			self.htpasswd = HTPasswd(htpasswd_file)
			self.ctimes["htpasswd"] = htpasswd_ctime

		# Normalize base_url and make it a member for easy access
		self.base_url = Path(self.get("www", "base_url"), absolute=True, append_slash=True)

		if self.version == 1:
			if os.environ.has_key('SCRIPT_FILENAME'):
				p = os.path.dirname(os.path.realpath(os.environ['SCRIPT_FILENAME']))
				self.base_path = Path(os.path.dirname(p.rstrip('/')))
			else:
				# no cgi script
				self.base_path = Path('')
			self.template_path = self.base_path + 'templates'

	def getpath(self, section, variable):
		path = Path(self.get(section, variable))
		if path.absolute:
			return path
		
		return self.base_path + path

	def get(self, section, variable):
		return self.cp.get(section, variable)

	def set(self, section, variable, value):
		self.cp.set(section, variable, value)

	def save(self):
		f = file(self.filename, 'w')
		self.cp.write(f)

class Config(object):
	"""Wrapper around ConfigData, so this is actually a Singleton.

	This is a subclass of object, for __getattribute__ to work."""

	instance = None # Class member, or "static"
	def __init__(self, filename=''):
		if not Config.instance:
			Config.instance = ConfigData(filename)

	def __getattribute__(self, attribute):
		if attribute == "_configdata_instance":
			# This is for the unittests, to see if our instance is really a
			# shared instance.
			return object.__getattribute__(self, "instance")
		return getattr(Config.instance, attribute)

	def __setattribute__(self, attribute, value):
		return setattr(Config.instance, attribute, value)

	def reinit(self):
		Config.instance.reinit()

