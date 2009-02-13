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

	def subcmd_fix(self, argv):
		if os.getuid() != 0:
			print '\nYou are not root so you can\'t change ownership\n'
			return

		if len(argv) > 0:
			self._fix(argv[0])
			return

		self._fix('')

	def _fix(self, unixuser):
		os.environ['SUBMIN_ENV'] = self.sa.env
		config = Config()
		items = [config.base_path]
		for filename in ['authz_file', 'access_file', 'userprop_file', 'repositories']:
			 items.append(config.getpath('svn', filename))

		items.append(config.getpath('backend', 'bindir'))

		apache = self._apache_user(unixuser)
 
		for item in items:
			s = str(item)
			try:
				if os.path.isdir(s):
					os.chmod(s, 0750)
				else:
					os.chmod(s, 0640)

				os.chown(s, apache.pw_uid, apache.pw_gid)

			except OSError:
				print ' *** Failed to change ownership of %s' % s
				print '     to apache user. Are you root?'

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
