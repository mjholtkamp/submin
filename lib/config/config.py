import ConfigParser
import os

from authz.authz import Authz
from authz.htpasswd import HTPasswd

from path.path import Path

class ConfigData:
	"""Upon construction, it should be checked if files need to be read."""
	cp = None
	authz = None
	htpasswd = None

	def __init__(self, filename=''):
		self.ctimes = {}
		self.ctimes["config"] = 0;
		self.ctimes["authz"] = 0;
		self.ctimes["userprop"] = 0;
		self.ctimes["htpasswd"] = 0;
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
		filename = self.filename
		if self.use_env:
			if not os.environ.has_key('SUBMIN_CONF'):
				raise Exception('SUBMIN_CONF environment not found')
			self.filename = os.environ['SUBMIN_CONF']
			if filename != self.filename:
				self.ctimes["config"] = 0;
				self.ctimes["authz"] = 0;
				self.ctimes["userprop"] = 0;
				self.ctimes["htpasswd"] = 0;
				filename = self.filename
		
		s_c = os.stat(self.filename)
		if not self.cp or s_c.st_ctime > self.ctimes["config"]:
			self.cp = ConfigParser.ConfigParser()
			self.cp.read(self.filename)
			self.ctimes["config"] = s_c.st_ctime

		# authz/userprop preparation
		authz_file = ''
		userprop_file = ''
		try:
			authz_file = self.get('svn', 'authz_file')
		except ConfigParser.NoSectionError, e:
			raise Exception(
				"Missing config section 'svn' in file %s" % filename)
		except ConfigParser.NoOptionError, e:
			raise Exception(
				"Missing config option 'authz_file' in file %s" % filename)

		try:
			userprop_file = self.get('svn', 'userprop_file')
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

		htpasswd_file = self.get('svn', 'access_file')
		htpasswd_ctime = self._ctime(htpasswd_file)
		if not self.htpasswd or htpasswd_ctime > self.ctimes["htpasswd"]:
			self.htpasswd = HTPasswd(htpasswd_file)
			self.ctimes["htpasswd"] = htpasswd_ctime

		# Normalize base_url and make it a member for easy access
		self.base_url = Path(self.get("www", "base_url"), append_slash=True)

		if os.environ.has_key('SCRIPT_FILENAME'):
			self.base_path = os.path.dirname(os.path.realpath(os.environ['SCRIPT_FILENAME']))
			self.base_path = os.path.dirname(self.base_path.rstrip('/'))
		else:
			# no cgi script
			self.base_path = ''

	def repositories(self):
		import glob, os.path
		reposdir = self.get('svn', 'repositories')
		_repositories = glob.glob(os.path.join(reposdir, '*'))
		repositories = []
		for repos in _repositories:
			if os.path.isdir(repos):
				repositories.append(repos[repos.rfind('/') + 1:])

		repositories.sort()

		return repositories

	def get(self, section, variable):
		return self.cp.get(section, variable)

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

