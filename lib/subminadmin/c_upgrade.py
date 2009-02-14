import os
from path.path import Path

class c_upgrade():
	'''Bring environment up-to-date with system installed version
Usage:
    upgrade   - Bring environment up-to-date with system installed version'''

	def __init__(self, sa, argv):
		self.sa = sa
		self.argv = argv
		self.systemdir = self._systemdir()

	def upgrade(self):
		dirs = ['bin', 'lib', 'templates', 'www']
		self._copy_dirs_with_backup(dirs)

	def _copy_dirs_with_backup(self, dirs):
		env = Path(self.sa.env)
		staticdir = env + 'static'
		backupdir = staticdir + '_backup_'
		try:
			os.makedirs(str(backupdir))
		except OSError:
			pass

		for d in dirs:
			os.system('rm -rf %s' % str(backupdir + d))
			self._rename(str(staticdir + d), str(backupdir + d))
			os.system("cp -r '%s' '%s'" % (str(self.systemdir + d), str(staticdir + d)))

	def _rename(self, src, dst):
		try:
			os.rename(src, dst)
		except OSError, e:
			if e.errno != 2: # No such file or directory
				raise

	def _systemdir(self):
		import inspect

		basefile = inspect.getmodule(self).__file__
		# Basefile will contain <basedir>/lib/subminadmin/c_upgrade.py
		subminadmin_basedir = os.path.dirname(basefile)
		lib_basedir = os.path.dirname(subminadmin_basedir)
		basedir = os.path.dirname(lib_basedir)
		return Path(basedir)

	def run(self):
		self.upgrade()
		self.sa.execute(['unixperms', 'fix'])
