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
			self.authz = Authz(authz_file, userprop_file)

		if not self.htpasswd:
			self.htpasswd = HTPasswd(self.get('svn', 'access_file'))

		# make sure base_url has a sane value
		if self.get('www', 'base_url') == '':
			self.set('www', 'base_url', '/')

		import os
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

		return repositories

	def get(self, section, variable):
		return self.cp.get(section, variable)
