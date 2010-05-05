import os
import glob
from submin.models import options

class DoesNotExistError(Exception):
	pass
class PermissionError(Exception):
	pass

def list():
	"""Returns a list of repositories"""
	repositories = []
	repository_names = _repositoriesOnDisk()
	repository_names.sort()

	for repos in repository_names:
		status = "ok"
		try:
			r = Repository(repos)
		except DoesNotExistError:
			pass
		except PermissionError:
			status = "permission denied"

		repositories.append({"name": repos, "status": status})

	return repositories

def _repositoriesOnDisk():
	reposdir = options.env_path('git_dir')
	reps = glob.glob(str(reposdir + '*'))
	repositories = []
	for rep in reps:
		if os.path.isdir(rep):
			repositories.append(rep[rep.rfind('/') + 1:])

	return repositories

def add(name):
	"""Create a new repository with name *name*"""
	reposdir = options.env_path('git_dir') + name
	if os.path.exists(reposdir):
		raise PermissionError("Could not create %s, already exists." % name)

	cmd = 'GIT_DIR="%s" git --bare init' % str(reposdir)
	(exitstatus, outtext) = commands.getstatusoutput(cmd)
	if exitstatus != 0:
		raise PermissionError(
			"External command 'GIT_DIR=\"%s\" git --bare init' failed: %s" % \
					(name, outtext))

class Repository(object):
	"""Internally, this class uses unicode to represent files and directories.
It is converted to UTF-8 (or other?) somewhere in the dispatcher."""

	def __init__(self, name):
		self.name = name
		self.signature = "### SUBMIN AUTOCONFIG, DO NOT ALTER FOLLOWING LINE ###\n"

		reposdir = options.env_path('git_dir')
		self.dir = reposdir + self.name
		self.url = str(reposdir + self.name)

		self.initialized = False
		self.dirs = self.branches()
		self.initialized = True

	def branches(self):
		return [x for x in
				glob.glob(str(self.dir + self.name + "refs" + "heads" + "*"))
				if os.path.isdir(x)]


	def remove(self, name):
		"""Removes repository *name*"""
		pass

	def subdirs(self, subdir):
		"""Get a list of subdirs of subdir *subdir* (root is "")
		Each dir is a dict with at least a property 'name'.
		
		Note: Git support in submin only returns branches, and only when
		      requesting subdirs for the root ("")
		"""
		if subdir == "":
			return self.branches()
		return [] # not supported for git

	def enableCommitEmails(self, enable):
		"""Enables sending of commit messages if *enable* is True."""
		pass

	def commitEmailsEnabled(self):
		"""Returns True if sendinf of commit messages is enabled."""
		pass

