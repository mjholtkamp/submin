import os
from submin.path.path import Path
from submin.subminadmin import common
from submin.models.exceptions import SendEmailError

class c_initenv():
	'''Initialize a new enviroment
Usage:
    initenv <email>                - Create environment interactively
    initenv <email> [option ...]   - Create environment from options

Mandatories:
    email                    - email address of the new admin user (needed
                               for account activation)
Options:
    svn_dir=<path>           - base path for svn repositories (default: svn)
    git_dir=<path>           - base path for git repositories (default: git)
    trac_dir=<path>          - dir for trac environments (default: trac)
    http_vhost=<fqdn>        - hostname of webserver (default: guessed)
    http_base=<url>          - base url (default: /)
    trac_url=<url>           - url to trac (default: trac)
    submin_url=<url>         - url to submin (default: submin)
    svn_url=<url>            - url to subversion repositories (default: svn)

Notes:
    The *_url arguments are all relative to http_base, unless they begin with
    "http://" or with "/".

    Paths are relative to environment directory, unless they begin with "/".'''

	needs_env = False

	def __init__(self, sa, argv):
		import socket
		self.sa = sa
		self.env = Path(self.sa.env)
		self.argv = argv
		self.defaults = {
			'svn_dir': Path('svn'),
			'git_dir': Path('git'),
			'trac_dir': Path('trac'),
			'http_base': Path('/'),
			'http_vhost': socket.getfqdn(),
			'trac_url': Path('trac'),
			'submin_url': Path('submin'),
			'svn_url': Path('svn'),
			'create_user': 'yes'
		}
		self.init_vars = {
			'conf_dir': Path('conf'),
			'hooks_dir': Path('hooks'),
		}
		self.init_vars.update({
			'authz': self.init_vars['conf_dir'] + Path('authz'),
			'htpasswd': self.init_vars['conf_dir'] + Path('htpasswd'),
		})
		self.email = None

	def prompt_user(self, prompt, key):
		defval = self.defaults[key]
		a = raw_input("%s [%s]> " % (prompt, defval))

		if a == '':
			self.set_init_var(key, defval)
			return

		self.set_init_var(key, a)

	def set_init_var(self, key, val):
		defval = self.defaults[key]
		if type(Path('')) == type(defval):
			p = Path(str(val), append_slash=defval.append_slash)
			self.init_vars[key] = p
			return

		self.init_vars[key] = val

	def interactive(self):
		print '''
Please provide a location for the Subversion repositories. For new Subversion
repositories, the default setting is ok. If the path is not absolute, it will
be relative to the submin environment. If you want to use an existing
repository, please provide the full pathname to the Subversion parent
directory (ie. /var/lib/svn).
'''
		self.prompt_user("Path to the repository?", 'svn_dir')

		print '''
Please provide a location for the git repositories. For new git repositories,
the default setting is ok. If the path is not absolute, it will be relative to
the submin environment. If you want to use an existing repository, please
provide the full pathname to the git parent directory (ie. /var/lib/git).
'''
		self.prompt_user("Path to the git repositories?", 'git_dir')

		print '''
Please provide a location for the parent dir of Trac environments. For a new
installation, the default setting is ok. If you don't want to use Trac, the
default setting is also ok. For existing Trac environments, please provide
the full path.
'''
		self.prompt_user("Path to trac environment?", 'trac_dir')

		print '''
Please provide a hostname that can be used to reach the web interface. This
hostname will be used in communication to the user (a link in email, links
in the web interface). The hostname should be a FQDN, so instead of 'foo' it
should be 'foo.example.com'. Please correct if the default is incorrect.
'''
		self.prompt_user("Hostname?", 'http_vhost')

		print '''
The HTTP path tells Submin where the website is located relative to the root.
This is needed for proper working of the website. Submin will be accesible
from <http base>/submin, Subversion will be accessible from <http base>/svn.
If you use Trac, it will be accessible from <http base>/trac.
'''
		self.prompt_user("HTTP base?", 'http_base')

		self.create_env()

	def create_dir(self, directory):
		"""Create a relative or absulute directory, if it doesn't exist
		already"""
		common.create_dir(self.env, directory)

	def create_env(self):
		"""This is called when all info is gathered"""
		for key, value in self.defaults.iteritems():
			if key not in self.init_vars:
				self.init_vars[key] = value

		try:
			self.create_dir(self.env)
			self.create_dir(self.init_vars['svn_dir'])
			self.create_dir(self.init_vars['git_dir'])
			self.create_dir(self.init_vars['conf_dir'])
			self.create_dir(self.init_vars['trac_dir'])
			self.create_dir(self.init_vars['hooks_dir'])
			self.create_dir(Path('auth'))
		except OSError:
			return # already printed error message

		self.sa.execute(['config', 'defaults'])

		# check http_base
		p = self.init_vars['http_base']
		if str(p) == "":
			self.init_vars['http_base'] = Path("/")

		# write changes to config
		from submin.models import options

		default_options = {
			'base_url_submin': self._get_url('submin_url'),
			'base_url_svn': self._get_url('svn_url'),
			'base_url_trac': self._get_url('trac_url'),
			'http_vhost': self.init_vars['http_vhost'],
			'auth_type': 'sql',
			'svn_dir': str(self.init_vars['svn_dir']),
			'git_dir': str(self.init_vars['git_dir']),
			'trac_dir': str(self.init_vars['trac_dir']),
			'svn_authz_file': str(self.init_vars['authz']),
		}
		for (key, value) in default_options.iteritems():
			options.set_value(key, value)

		# add a user
		from submin.models import user
		
		if self.init_vars['create_user'] == "yes":
			# add an admin user
			u = user.add('admin', self.email, send_mail=False)
			u.is_admin = True
			try:
				u.prepare_password_reset('submin2-admin')
			except SendEmailError as e:
				print 'WARNING: Could not send an e-mail, please install a mail server'
				print 'WARNING: You can request a password reset for "admin" on the login page'

		self.sa.execute(['upgrade', 'hooks', 'no-fix-unixperms'])
		self.sa.execute(['unixperms', 'fix'])
		self.sa.execute(['apacheconf', 'create', 'all'])
		self.sa.execute(['trac', 'init'])

	def _get_url(self, key):
		p = self.init_vars[key]
		if p.absolute or str(p).startswith("http://"):
			return str(p)

		return str(self.init_vars['http_base'] + p)

	def run(self):
		if os.path.exists(str(self.env)):
			print "Directory already exists, won't overwrite"
			return False

		if len(self.argv) < 1:
			self.sa.execute(['help', 'initenv'])
			return True

		self.email = self.argv[0]

		if len(self.argv) < 2:
			try:
				self.interactive()
			except KeyboardInterrupt:
				print
				return False
			return True

		for arg in self.argv[1:]:
			if '=' not in arg:
				self.sa.execute(['help', 'initenv'])
				return False

			(key, val) = arg.split('=', 1)
			if key not in self.defaults:
				print "\nSorry, I don't understand `%s':\n" % key
				self.sa.execute(['help', 'initenv'])
				return False

			self.set_init_var(key, val)

		self.create_env()
		return True
