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
		from models.user import User

		# get filename
		htpasswd_file = config.get('svn', 'access_file')
		userprop_file = config.get('svn', 'userprop_file')
		
		# read files
		htpasswd = file(htpasswd_file).readlines()
		userprop = self.read_ini(userprop_file)

		# add users
		for line in htpasswd:
			(user, password) = line.strip('\n').split(':')
			u = User.add(user, password)
			if userprop.has_section(user):
				if userprop.has_option(user, 'email'):
					u.email = userprop.get(user, 'email')

	def write_groups(self, config):
		from models.group import Group

		# get filename
		authz_file = config.get('svn', 'authz_file')
		
		# read file
		cp = self.read_ini(authz_file)
		
		# get groups
		groups = cp.options('groups')
		for group in groups:
			members = cp.get('groups', group)
			g = Group.add(group)
			for member in members:
				# convert to userid
				#g.add_member(member)
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
