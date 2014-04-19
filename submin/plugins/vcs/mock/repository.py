import os
import glob
from submin.models import options
from submin.models.repository import DoesNotExistError, PermissionError
from submin.common.osutils import mkdirs

display_name = "Mock"

def list():
	"""Returns a list of repositories"""
	repositories = []
	repository_names = _repositoriesOnDisk()
	repository_names.sort()

	for repos in repository_names:
		status = "ok"
		r = None
		try:
			r = Repository(repos)
		except DoesNotExistError:
			pass
		except PermissionError:
			status = "permission denied"

		repositories.append({"name": r.display_name(), "status": status})

	return repositories

def _repositoriesOnDisk():
	reposdir = options.env_path('mock_dir', default="mock")
	reps = glob.glob(str(reposdir + '*.mock'))
	repositories = []
	for rep in reps:
		if os.path.isdir(rep):
			name = rep[rep.rfind('/') + 1:]
			repositories.append(unicode(name, 'utf-8'))

	return repositories

def add(name):
	"""Create a new repository with name *name*"""
	if not name.endswith(".mock"):
		name += ".mock"
	reposdir = options.env_path('mock_dir', default='mock') + name

	if os.path.exists(str(reposdir)):
		raise PermissionError("Could not create %s, already exists." % name)

	mkdirs(reposdir)

def directory(name):
	return name

def url(name):
	return name

class Repository(object):
	"""Internally, this class uses unicode to represent files and directories.
It is converted to UTF-8 (or other?) somewhere in the dispatcher."""

	def __init__(self, name):
		self.name = name
		if not self.name.endswith(".mock"):
			self.name += ".mock"

		reposdir = options.env_path('mock_dir', default='mock')
		self.dir = reposdir + self.name
		self.url = str(reposdir + self.name)

		if not os.path.exists(str(self.dir)):
			raise DoesNotExistError(str(self.dir))

		self.initialized = False
		self.dirs = self.branches()
		self.initialized = True

	def display_name(self):
		return self.name[:-5]

	def branches(self):
		return []

	def subdirs(self, subdir):
		"""Get a list of subdirs of subdir *subdir* (root is "")
		Each dir is a dict with at least a property 'name'.
		"""
		if str(subdir) == "":
			return self.branches()
		return [] # not supported for Mock

	def remove(self):
		"""Removes repository *name*"""
		if not self.dir.absolute:
			raise Exception("Error, repository path is relative, this should be fixed")

		if not self.dir.exists():
			raise Exception("Repository %s does not exist." % self.name)

		os.removedirs(self.dir)

	def enableCommitEmails(self, enable):
		"""Enables sending of commit messages if *enable* is True."""
		pass

	def commitEmailsEnabled(self):
		"""Returns True if sending of commit messages is enabled."""
		return False

	def enableTracCommitHook(self, enable):
		pass

	def tracCommitHookEnabled(self):
		"""Returns True if trac sync is enabled."""
		return False

	def __str__(self):
		return self.display_name()
