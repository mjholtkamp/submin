import os
import glob
import shutil

from submin.path.path import Path
from submin.common.osutils import mkdirs

class c_upgrade():
	'''Upgrades your environment to the latest version
Usage:
	upgrade database      - Upgrade the database to the latest version
    upgrade hooks         - Upgrade all by submin provided hooks to the
                            latest version'''

	def __init__(self, sa, argv):
		self.sa = sa
		self.argv = argv

		self.env = Path(self.sa.env)

	def find_hook_dirs(self):
		from submin.models import options

		hooks_dir = options.static_path("hooks") + "submin"
		event_dirs = glob.glob(str(hooks_dir + "*"))
		event_dirs = [os.path.basename(x) for x in event_dirs
				if os.path.isdir(x)]
		return event_dirs

	def create_dir(self, directory):
		"""Create a relative or absulute directory, if it doesn't exist already"""
		if not directory.absolute:
			directory = self.env + directory

		if not os.path.exists(str(directory)):
			try:
				mkdirs(str(directory), mode=0700)
			except OSError, e:
				print 'making dir %s failed, do you have permissions?' % \
						str(directory)
				raise e

	def remove_system_hooks(self):
		from submin.models import options

		env_event_dir = options.env_path() + "hooks"
		for script in glob.glob(str(env_event_dir + "*/[3-6]*")):
			try:
				os.unlink(script)
			except OSError, e:
				print 'updating hook %s failed, do you have permissions?' % \
						script
				raise e

	def copy_system_hooks(self, event_dir):
		from submin.models import options

		sys_event_dir = options.static_path("hooks") + "submin" + event_dir
		env_event_dir = options.env_path() + "hooks" + event_dir
		for script in glob.glob(str(sys_event_dir + "[3-6]*")):
			try:
				shutil.copy(script, str(env_event_dir))
			except IOError, e:
				print 'updating hook %s failed, do you have permissions?' % \
						script

	def subcmd_database(self, argv):
		from submin.models import storage
		new_version = storage.database_evolve(verbose=True)

	def subcmd_hooks(self, argv):
		# The upgrade hooks command just copies the hooks to the environment
		# directory. It does not check if the system-provided hooks are
		# modified and thus overwritten.
		event_dirs = self.find_hook_dirs()
		self.remove_system_hooks()
		for event_dir in event_dirs:
			self.create_dir(self.env + "hooks" + event_dir)
			self.copy_system_hooks(event_dir)

		if "no-fix-unixperms" not in argv:
			self.sa.execute(['unixperms', 'fix'])

	def run(self):
		if len(self.argv) < 1:
			self.sa.execute(['help', 'upgrade'])
			return

		try:
			subcmd = getattr(self, 'subcmd_%s' % self.argv[0])
		except AttributeError:
			self.sa.execute(['help', 'upgrade'])
			return

		subcmd(self.argv[1:])
