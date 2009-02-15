import os
from config.config import Config

class c_unixperms():
	'''Commands regarding unix permissions
Usage:
    unixperms fix         - sets permissions and ownerships to sane values
    unixperms fix <user>  - sets sane permissions and unix owner to <user>'''

	def __init__(self, sa, argv):
		self.sa = sa
		self.argv = argv
		self.root = True

	def subcmd_fix(self, argv):
		if os.getuid() != 0:
			print '''
To also set ownerships properly, execute as root:

    submin-admin unixperms fix

This should also remove possible following warnings.
'''
			self.root = False

		if len(argv) > 0:
			self._fix(argv[0])
			return

		self._fix('')

	def _fix(self, unixuser):
		os.environ['SUBMIN_ENV'] = self.sa.env
		config = Config()

		nonroots = []
		nonroots.append(config.base_path + 'auth')
		nonroots.append(config.getpath('trac', 'basedir'))
		for filename in ['authz_file', 'access_file', 'userprop_file', 'repositories']:
			 nonroots.append(config.getpath('svn', filename))

		apache = self._apache_user(unixuser)
		root = self._apache_user('root')

		self._recurse_change(str(config.base_path), root.pw_uid, apache.pw_gid)
		for nonroot in nonroots:
			item = str(nonroot)
			self._recurse_change(item, apache.pw_uid, apache.pw_gid)
			if os.path.isfile(item):
				st = os.stat(os.path.dirname(item))
				if st.st_uid != apache.pw_uid:
					print '''\
*** WARN: file should be writable by apache user, but parent directory is not.
             (%s)''' % item

	def _recurse_change(self, directory, user, group):
		self._change_item(directory, user, group)
		for root, dirs, files in os.walk(directory):
			for f in files:
				self._change_item(os.path.join(root, f), user, group)
			for d in dirs:
				path = os.path.join(root, d)
				self._recurse_change(path, user, group)

	def _change_item(self, item, user, group):
		try:
			permission = 0640
			if os.path.isdir(item):
				permission = 0750
			(root, ext) = os.path.splitext(item)
			if ext == '.cgi' or ext == '.wsgi':
				permission = 0750

			os.chmod(item, permission)
		except OSError:
			print ' *** Failed to change permissions of %s' % s
			print '     Do you have the right permissions?'

		if self.root:
			try:
				os.chown(item, user, group)
			except OSError:
				print ' *** Failed to change ownership of %s' % s

	def _apache_user(self, preferred=''):
		from pwd import getpwnam
		users = []
		# _www in OS X :)
		for user in [preferred, 'www-data', 'httpd', 'apache', '_www']:
			pwd = ()
			try:
				pwd = getpwnam(user)
			except KeyError, e:
				pass
			else:
				return pwd

		return

	def run(self):
		if len(self.argv) < 1:
			self.sa.execute(['help', 'unixperms'])
			return

		try:
			subcmd = getattr(self, 'subcmd_%s' % self.argv[0])
		except AttributeError:
			self.sa.execute(['help', 'unixperms'])
			return

		subcmd(self.argv[1:])
