from path.path import Path
import os, sys

class c_config():
	'''Commands to change config
Usage:
	config defaults                 - create config with defaults
	config get                      - list everything
	config get <option>             - get config value in section
	config set <option> <value>     - set config value in section'''

	def __init__(self, sa, argv):
		self.sa = sa
		self.argv = argv
		os.environ['SUBMIN_ENV'] = self.sa.env
		self.settings_path = str(Path(self.sa.env) + 'conf' + 'settings.py')

	def subcmd_defaults(self, argv):
		self.settings_defaults(self.settings_path)

	def _printkeyvalue(self, options, key, value, width):
		formatstring = "%%-%us %%s" % (width + 1)
		print formatstring % (key, value)

	def subcmd_get(self, argv):
		import models.options
		o = models.options.Options()
		if len(argv) == 1:
			value = o.value(argv[0])
			self._printkeyvalue(o, argv[0], value, len(argv[0]))
		else:
			options = o.options()
			options.sort()
			maxlen = 0
			for arg in options:
				if len(arg[0]) > maxlen: maxlen = len(arg[0])

			for arg in options:
				self._printkeyvalue(o, arg[0], arg[1], maxlen)

	def subcmd_set(self, argv):
		if len(argv) != 2:
			self.sa.execute(['help', 'config'])
			return

		import models.options
		o = models.options.Options()
		o.set_value(argv[0], argv[1])

	def session_salt(self):
		import random
		salts = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789./'
		salt = ''
		rand = random.Random()
		for i in range(16):
			salt += rand.choice(salts)

		return salt

	def settings_defaults(self, filename):
		# write the bootstrap settings file
		submin_settings = '''
import os
backend = "sql"
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
		from models import backend
		backend.open()
		backend.setup()

		# And now we can use the models
		#from models.options import Options
		import models.options

		o = models.options.Options()
		http_base = ''
		options = {
			'base_url_submin': http_base + '/submin',
			'base_url_svn': http_base + '/svn',
			'base_url_trac': http_base + '/trac',
			'auth_type': 'sql',
			'dir_svn': 'svn',
			'dir_trac': 'trac',
			'dir_bin': 'static/bin',
			'enabled_trac': 'no',
			'session_salt': self.session_salt(),
			'env_path': '/bin:/usr/bin:/usr/local/bin:/opt/local/bin',
		}
		for (key, value) in options.iteritems():
			o.set_value(key, value)

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
