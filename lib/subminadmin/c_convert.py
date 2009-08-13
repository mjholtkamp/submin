import os

class c_convert():
	'''Create a new configuration from an old-style config
Usage:
    convert <old-config-file>   - Interactively create new config from old'''

	def __init__(self, sa, argv):
		self.sa = sa
		self.argv = argv
		os.environ['SUBMIN_ENV'] = self.sa.env

	def read_ini(self, filename):
		import ConfigParser
		cp = ConfigParser.ConfigParser()
		cp.read(filename)
		return cp

	def init_backend(self):
		self.sa.execute(['config', 'defaults'])

	def write_options(self, config):
		from models.options import Options
		o = Options()

		options = {
			'base_url_submin': ('www', 'base_url'),
			'base_url_svn': ('www', 'svn_base_url'),
			'base_url_trac': ('www', 'trac_base_url'),
			'dir_svn': ('svn', 'repositories'),
			'dir_trac': ('trac', 'basedir'),
			'dir_bin': ('backend', 'bindir'),
			'session_salt': ('generated', 'session_salt'),
			'env_path': ('backend', 'path'),
		}
		for (key, section_option) in options.iteritems():
			value = config.get(section_option[0], section_option[1])
			o.set_value(key, value)

	def write_users(self, config):
		pass

	def write_groups(self, config):
		pass

	def convert(self, old_config_file):
		config = self.read_ini(old_config_file)
		self.init_backend()
		self.write_options(config)
		self.write_users(config)
		self.write_groups(config)

	def run(self):
		if len(self.argv) != 1:
			self.sa.execute(['help', 'convert'])
			return

		self.convert(self.argv[0])
