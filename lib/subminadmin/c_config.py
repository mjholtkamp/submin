from path.path import Path
from config.config import ConfigData
import os

class c_config():
	'''Commands to change config
Usage:
	config defaults                           - create config with defaults
	config get                                - list everything
	config get <section>                      - list options in section
	config get <section> <option>             - get config value in section
	config set <section> <option> <value>     - set config value in section'''

	def __init__(self, sa, argv):
		self.sa = sa
		self.argv = argv
		os.environ['SUBMIN_ENV'] = self.sa.env

	def subcmd_defaults(self, argv):
		filename = str(Path(self.sa.env) + 'conf' + 'submin.ini')
		self.submin_ini_defaults(filename)

	def subcmd_get(self, argv):
		c = ConfigData()

	def subcmd_set(self, argv):
		if len(argv) != 3:
			self.sa.execute(['help', 'config'])
			return

		c = ConfigData()
		c.set(argv[0], argv[1], argv[2])
		c.save()

	def session_salt(self):
		import random
		salts = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789./'
		salt = ''
		rand = random.Random()
		for i in range(16):
			salt += rand.choice(salts)

		return salt

	def submin_ini_defaults(self, filename):
		vars = {
			'authz': 'authz',
			'userprop': 'userprop.conf',
			'htpasswd': 'htpasswd',
			'svn dir': 'svn',
			'http base': '',
			'bin dir': 'bin',
			'session salt': self.session_salt()
		}

		submin_ini = '''[svn]
authz_file = %(authz)s
userprop_file = %(userprop)s
access_file = %(htpasswd)s
repositories = %(svn dir)s

[www]
base_url = %(http base)s/submin
svn_base_url = %(http base)s/svn
trac_base_url = %(http base)s/trac

[backend]
bindir = %(bin dir)s

[generated]
session_salt = %(session salt)s
''' % vars

		file(filename, 'w').write(submin_ini)

	def run(self):
		if len(self.argv) < 1:
			self.sa.execute(['help', 'config'])
			return

		try:
			subcmd = getattr(self, 'subcmd_%s' % self.argv[0])
		except AttributeError:
			self.sa.execute(['help', 'config'])
			return

		subcmd(self.argv[1:])
