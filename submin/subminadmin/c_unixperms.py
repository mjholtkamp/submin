from submin.path.path import Path
import os

class c_unixperms():
	'''Commands regarding unix permissions
Usage:
    unixperms fix         - sets permissions and ownerships to sane values
    unixperms fix <user>  - sets sane permissions and unix owner to <user>'''

	def __init__(self, sa, argv):
		self.sa = sa
		self.argv = argv
		self.root = True
		self.fix_mode_dirs = ['cgi-bin', 'conf']

	def subcmd_fix(self, argv):
		if os.getuid() != 0:
			print '''
To set permissions and ownerships properly, execute:

    sudo submin2-admin %s unixperms fix

This should also remove possible following warnings.
''' % self.sa.env
			self.root = False

		if len(argv) > 0:
			self._fix(argv[0])
			return

		self._fix('')

	def _fix(self, unixuser):
		base_dir = Path(self.sa.env)

		apache = self.apache_user(unixuser)
		directory = str(base_dir)
		user = apache.pw_uid
		group = apache.pw_gid

		self.fix_mode_paths = [os.path.join(directory, x) for x in self.fix_mode_dirs]

		if not self._change_item(directory, user, group):
			return

		for root, dirs, files in os.walk(directory):
			for f in files:
				path = os.path.join(root, f)
				self._change_item(path, user, group)
			for d in dirs:
				path = os.path.join(root, d)
				self._change_item(path, user, group)

	def _change_item(self, item, user, group):
		success = True
		do_chmod = False
		for path in self.fix_mode_paths:
			if path in item:
				do_chmod = True

		if do_chmod:
			try:
				permission = 0640
				if os.path.isdir(item):
					permission = 0750
				(root, ext) = os.path.splitext(item)
				if ext in ('.cgi', '.wsgi', '.fcgi'):
					permission = 0750

				os.chmod(item, permission)
			except OSError:
				print ' *** Failed to change permissions of %s' % item
				print '     Do you have the right permissions?'
				success = False

		if self.root:
			try:
				os.chown(item, user, group)
			except OSError:
				print ' *** Failed to change ownership of %s' % item
				success = False

		return success

	def apache_user(self, preferred=''):
		"""Returns most probably www-user"""
		from pwd import getpwnam
		users = []
		known = [preferred, 'www-data', 'httpd', 'apache', '_www', 
					'wwwrun', 'www']
		for user in known:
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
