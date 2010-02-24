import os
from submin.models.exceptions import UserExistsError, GroupExistsError
from submin.models.exceptions import MemberExistsError
from submin.models.user import FakeAdminUser

class c_convert():
	'''Create a new configuration from an old-style config
Usage:
    convert <old-config-file>   - Interactively create new config from old'''

	needs_env = False

	def __init__(self, sa, argv):
		self.sa = sa
		self.argv = argv
		os.environ['SUBMIN_ENV'] = self.sa.env

	def read_ini(self, filename):
		import ConfigParser
		cp = ConfigParser.ConfigParser()
		cp.read(filename)
		return cp

	def init_storage(self):
		self.sa.execute(['config', 'defaults'])

	def write_options(self, config):
		from submin.models.options import Options
		o = Options()

		options = {
			'base_url_submin': ('www', 'base_url'),
			'base_url_svn': ('www', 'svn_base_url'),
			'base_url_trac': ('www', 'trac_base_url'),
			'svn_dir': ('svn', 'repositories'),
			'trac_dir': ('trac', 'basedir'),
			'dir_bin': ('backend', 'bindir'),
			'session_salt': ('generated', 'session_salt'),
			'env_path': ('backend', 'path'),
			'svn_authz_file': ('svn', 'authz_file'),
		}
		for (key, section_option) in options.iteritems():
			value = config.get(section_option[0], section_option[1])
			o.set_value(key, value)

	def write_users(self, config):
		from submin.models.user import User

		# get filename
		htpasswd_file = config.get('svn', 'access_file')
		userprop_file = config.get('svn', 'userprop_file')

		# read files
		htpasswd = file(htpasswd_file).readlines()
		userprop = self.read_ini(userprop_file)

		# fake an admin user
		fake_admin = FakeAdminUser()

		# add users
		for line in htpasswd:
			(user, password) = line.strip('\n').split(':')
			try:
				u = User.add(user)
			except UserExistsError:
				u = User(user)

			u.set_md5_password(password)

			if userprop.has_section(user):
				if userprop.has_option(user, 'email'):
					u.email = userprop.get(user, 'email')
				if userprop.has_option(user, 'notifications_allowed'):
					allowed = userprop.get(user, 'notifications_allowed')
					allowed = [x.strip() for x in allowed.split(',')]

					enabled = []
					if userprop.has_option(user, 'notifications_enabled'):
						enabled = userprop.get(user, 'notifications_enabled')
						enabled =  [x.strip() for x in enabled.split(',')]

					repositories = {}
					for repos in allowed:
						repos_enabled = False
						if repos in enabled:
							repos_enabled = True
						repositories[repos] = {'allowed': True, 'enabled': repos_enabled}

					# add notifications
					for repos, details in repositories.iteritems():
						allowed = False
						enabled = False
						if details['allowed']:
							allowed = True
						if details['enabled']:
							enabled = True
						u.set_notification(repos, allowed, enabled, fake_admin)

	def write_groups(self, config):
		from submin.models.group import Group
		from submin.models.user import User

		# get filename
		authz_file = config.get('svn', 'authz_file')

		# read file
		cp = self.read_ini(authz_file)

		# get groups
		groups = cp.options('groups')
		for group in groups:
			members = [x.strip() for x in cp.get('groups', group).split(',')]
			try:
				g = Group.add(group)
			except GroupExistsError:
				g = Group(group)

			for member in members:
				u = User(member)
				try:
					g.add_member(u)
				except MemberExistsError:
					pass
				if group == "submin-admins":
					u.is_admin = True

	def write_permissions(self, config):
		from submin.models.permissions import Permissions
		p = Permissions()

		# get filename
		authz_file = config.get('svn', 'authz_file')

		# read file
		cp = self.read_ini(authz_file)

		# get all sections
		for section in cp.sections():
			if section == 'groups':
				continue

			repository = ''
			path = ''
			if ':' in section:
				repository, path = section.split(':', 2)

			for name in cp.options(section):
				permission = cp.get(section, name)
				if name[0] == '@':
					name_type = 'group'
					name = name[1:]
				elif name == '*':
					name_type = 'all'
				else:
					name_type = 'user'

				p.add_permission(repository, "svn", path, name, name_type, permission)

	def convert(self, old_config_file):
		config = self.read_ini(old_config_file)
		self.init_storage()
		self.write_options(config)
		self.write_users(config)
		self.write_groups(config)
		self.write_permissions(config)

	def run(self):
		if len(self.argv) != 1:
			self.sa.execute(['help', 'convert'])
			return

		self.convert(self.argv[0])
