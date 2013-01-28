import os, sys

from submin.path.path import Path
from submin.models.exceptions import StorageAlreadySetup
from submin.subminadmin import common

class c_config():
	'''Commands to change config
Usage:
	config defaults                 - create config with defaults
	config get                      - list everything
	config get <option>             - get config value in section
	config set <option> <value>     - set config value in section
	config unset <option>           - remove option'''

	needs_env = False

	def __init__(self, sa, argv):
		self.sa = sa
		self.env = Path(self.sa.env)
		self.argv = argv
		self.settings_path = str(Path(self.sa.env) + 'conf' + 'settings.py')

	def subcmd_defaults(self, argv):
		self.settings_defaults(self.settings_path)

	def _printkeyvalue(self, key, value, width):
		formatstring = "%%-%us %%s" % (width + 1)
		print formatstring % (key, value)

	def subcmd_get(self, argv):
		from submin.models import options
		self.sa.ensure_storage()

		if len(argv) == 1:
			value = options.value(argv[0])
			self._printkeyvalue(argv[0], value, len(argv[0]))
		else:
			all_options = options.options()
			all_options.sort()
			maxlen = 0
			for arg in all_options:
				if len(arg[0]) > maxlen: maxlen = len(arg[0])

			for arg in all_options:
				self._printkeyvalue(arg[0], arg[1], maxlen)

	def subcmd_set(self, argv):
		from submin.models import options
		self.sa.ensure_storage()

		if len(argv) < 2:
			self.sa.execute(['help', 'config'])
			return

		options.set_value(argv[0], ' '.join(argv[1:]))

	def subcmd_unset(self, argv):
		from submin.models import options
		self.sa.ensure_storage()

		if len(argv) == 1:
			options.unset_value(argv[0])

	def session_salt(self):
		import random
		salts = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789./'
		salt = ''
		rand = random.Random()
		for i in range(16):
			salt += rand.choice(salts)

		return salt

	def vcs_plugins(self):
		import pkgutil, os
		# __file__ returns <submin-dir>/subminadmin/c_config.py
		libdir = os.path.dirname(os.path.dirname(__file__))
		vcsdir = os.path.join(libdir, 'plugins', 'vcs')
		return [name for _, name, _ in pkgutil.iter_modules([vcsdir])]

	def settings_defaults(self, filename):
		# write the bootstrap settings file
		submin_settings = '''
import os
storage = "sql"
sqlite_path = os.path.join(os.path.dirname(__file__), "submin.db")
'''

		dirname = os.path.dirname(filename)
		try:
			os.makedirs(dirname)
		except OSError, e:
			if e.errno == 17: # file exists
				pass

		file(filename, 'w').write(submin_settings)

		# after writing the bootstrap file, we setup all models
		self.sa.ensure_storage()
		from submin.models import storage
		storage.database_evolve()

		# And now we can use the models
		from submin.models import options
		import platform

		http_base = ''
		default_options = {
			'base_url_submin': http_base + '/submin',
			'base_url_svn': http_base + '/svn',
			'base_url_git': http_base + '/git',
			'base_url_trac': http_base + '/trac',
			'http_vhost': platform.node(),
			'auth_type': 'sql',
			'svn_dir': 'svn',
			'git_dir': 'git',
			'trac_dir': 'trac',
			'dir_bin': 'static/bin',
			'enabled_trac': 'no',
			'session_salt': self.session_salt(),
			'env_path': '/bin:/usr/bin:/usr/local/bin:/opt/local/bin',
			'vcs_plugins': 'svn',
		}
		for (key, value) in default_options.iteritems():
			options.set_value(key, value)
		self.generate_cgi()

	def generate_cgi(self):
		common.create_dir(self.env, Path('cgi-bin'))

		fname = self.env + "cgi-bin" + "submin.cgi"
		fp = open(str(fname), "w+")

		suggestion = '/path/to/submin'
		if os.environ.has_key("PYTHONPATH"):
			suggestion = os.path.abspath(os.environ["PYTHONPATH"].split(":")[0])

		fp.write("""#!/usr/bin/env python

# If you installed submin in a non-standard path, uncomment the two lines below
# and insert your submin path.
#import sys
#sys.path.append("%s")

from submin.dispatch.cgirunner import run
run()
""" % suggestion)
		fp.close()
		os.chmod(str(fname), 0755)

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
