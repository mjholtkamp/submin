import os
from submin.models.exceptions import UserExistsError, GroupExistsError
from submin.models.exceptions import MemberExistsError
from submin.path.path import Path

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
		from submin.models import options
		from ConfigParser import NoOptionError, NoSectionError

		cfg = {
			'base_url_submin': ('www', 'base_url'),
			'base_url_svn': ('www', 'svn_base_url'),
			'base_url_trac': ('www', 'trac_base_url'),
			'svn_dir': ('svn', 'repositories'),
			'trac_dir': ('trac', 'basedir'),
			'dir_bin': ('backend', 'bindir'),
			'session_salt': ('generated', 'session_salt'),
			'env_path': ('backend', 'path'),
		}
		for (key, section_option) in cfg.iteritems():
			try:
				value = config.get(section_option[0], section_option[1])
				options.set_value(key, value)
			except (NoOptionError, NoSectionError):
				pass # fallback to the defaults set before

		options.set_value('svn_authz_file', 'conf/authz')

	def write_users(self, config):
		from submin.models import user

		# get filename
		htpasswd_file = config.get('svn', 'access_file')
		userprop_file = config.get('svn', 'userprop_file')

		# read files
		htpasswd = file(htpasswd_file).readlines()
		userprop = self.read_ini(userprop_file)

		from submin.models.user import FakeAdminUser

		# fake an admin user
		fake_admin = FakeAdminUser()

		# add users
		for line in htpasswd:
			(username, md5_password) = line.strip('\n').split(':')
			try:
				# This is a hack. We need to supply an email-address and
				# if we don't supply a password, user.add() will try to send
				# an email. Both email and password will be set later.
				u = user.add(username, email="a@a.a", password=md5_password)
			except UserExistsError:
				u = user.User(username)

			u.set_md5_password(md5_password)

			if userprop.has_section(username):
				if userprop.has_option(username, 'email'):
					u.email = userprop.get(username, 'email')
				if userprop.has_option(username, 'notifications_allowed'):
					allowed = userprop.get(username, 'notifications_allowed')
					allowed = [x.strip() for x in allowed.split(',')]

					enabled = []
					if userprop.has_option(username, 'notifications_enabled'):
						enabled = userprop.get(username, 'notifications_enabled')
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
		from submin.models import group
		from submin.models import user

		# get filename
		authz_file = config.get('svn', 'authz_file')

		# read file
		cp = self.read_ini(authz_file)

		# get groups
		groups = cp.options('groups')
		for groupname in groups:
			members = [x.strip() for x in cp.get('groups', groupname).split(',')]
			try:
				g = group.add(groupname)
			except GroupExistsError:
				g = group.Group(groupname)

			for member in members:
				u = user.User(member)
				try:
					g.add_member(u)
				except MemberExistsError:
					pass
				if groupname == "submin-admins":
					u.is_admin = True

	def write_permissions(self, config):
		from submin.models import permissions

		# get filename
		authz_file = config.get('svn', 'authz_file')

		# read file
		cp = self.read_ini(authz_file)

		from submin.models.repository import DoesNotExistError

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

				try:
					permissions.add(repository, "svn", path, name,
							name_type, permission)
				except DoesNotExistError:
					print "Could not add permissions for repository %s, skipping" % repository

	def convert(self, old_config_file):
		config = self.read_ini(old_config_file)
		self.init_storage()
		self.write_options(config)
		self.write_users(config)
		self.write_groups(config)
		self.write_permissions(config)
		
		# final initialize (for convenience)
		self.sa.execute(['upgrade', 'hooks', 'no-fix-unixperms'])
		self.sa.execute(['unixperms', 'fix'])
		confdir = Path(self.sa.env) + 'conf'
		cgiconf = confdir + 'apache.cgi.conf'
		wsgiconf = confdir + 'apache.wsgi.conf'
		self.sa.execute(['apacheconf', 'create', 'cgi', str(cgiconf)])
		self.sa.execute(['apacheconf', 'create', 'wsgi', str(wsgiconf)])

	def run(self):
		if len(self.argv) != 1:
			self.sa.execute(['help', 'convert'])
			return

		self.convert(self.argv[0])
