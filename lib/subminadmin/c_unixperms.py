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
			print '''To also set ownerships properly, execute as root:
    submin-admin unixperms fix
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
		nonroots.append(config.base_path)
		nonroots.append(config.getpath('trac', 'basedir'))
		for filename in ['authz_file', 'access_file', 'userprop_file', 'repositories']:
			 nonroots.append(config.getpath('svn', filename))

		roots = []
		roots.append(config.base_path + 'conf')
		roots.append(config.base_path + 'conf' + 'submin.ini')
		roots.append(config.getpath('backend', 'bindir'))

		apache = self._apache_user(unixuser)
		root = self._apache_user('root')

		self._change_items(nonroots, apache)
		self._change_items(roots, root)

	def _change_items(self, items, user):
		for item in items:
			s = str(item)
			try:
				if os.path.isdir(s):
					os.chmod(s, 0750)
				else:
					os.chmod(s, 0640)
			except OSError:
				print ' *** Failed to change permissions of %s' % s
				print '     Do you have the right permissions?'

			if self.root:
				try:
					os.chown(s, user.pw_uid, user.pw_gid)
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
