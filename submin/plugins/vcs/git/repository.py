import os
import glob
import commands
from submin.models import options
from submin.models.exceptions import UnknownKeyError, MissingConfig
from submin.models.repository import DoesNotExistError, PermissionError
from submin.plugins.vcs.git import remote
from submin.subminadmin.git.common import signature as hook_signature
from submin.common import shellscript

display_name = "Git"
has_path_permissions = False

def list():
	"""Returns a list of repositories"""
	repositories = []
	repository_names = sorted(_repositoriesOnDisk())

	for repos in repository_names:
		status = "ok"
		r = None
		try:
			r = Repository(repos)
		except DoesNotExistError:
			pass
		except PermissionError:
			status = "permission denied"

		repositories.append({"name": r.name, "status": status})

	return repositories

def _repositoriesOnDisk():
	reposdir = options.env_path('git_dir')
	reps = glob.glob(str(reposdir + '*.git'))
	repositories = []
	for rep in reps:
		if os.path.isdir(rep):
			name = rep[rep.rfind('/') + 1:]
			name = name[:-4] # chop off '.git'
			repositories.append(unicode(name, 'utf-8'))

	return repositories

def add(name):
	"""Create a new repository with name *name*"""
	reposdir = directory(name)
	if os.path.exists(str(reposdir)):
		raise PermissionError("Could not create %s, already exists." % name)

	try:
		remote.execute("create %s" % name)
	except remote.NonZeroExitStatus as e:
		raise PermissionError(
			"External command 'GIT_DIR=\"%s\" git --bare init' failed: %s" % \
					(name, e))

def url(reposname):
	try:
		git_user = options.value("git_user")
		git_host = options.value("git_ssh_host")
	except UnknownKeyError as e:
		raise MissingConfig(
			'Please make sure both git_user and git_ssh_host settings are set')

	git_port = options.value("git_ssh_port", "22")
	if git_port == "22":
		git_port = ""
	else:
		git_port = ":%s" % git_port
	return 'ssh://%s@%s%s/%s.git' % (git_user, git_host, git_port, reposname)

def directory(reposname):
	# FIXME: encoding?
	base_dir = options.env_path('git_dir')
	reposdir = base_dir + (reposname + '.git')
	# We could use realpath to check, but we don't want to prevent usage of
	# symlinks in their git directory
	if not os.path.normpath(reposdir).startswith(os.path.normpath(base_dir)):
		raise Exception('Git directory outside base path');

	return reposdir


class Repository(object):
	"""Internally, this class uses unicode to represent files and directories.
It is converted to UTF-8 (or other?) somewhere in the dispatcher."""

	def __init__(self, name):
		self.name = name
		self.dir = directory(name)

		if not self.dir.exists():
			raise DoesNotExistError(str(self.dir))

		self.initialized = False
		self.dirs = self.branches()
		self.initialized = True

	def branches(self):
		dirname = str(self.dir + "refs" + "heads" + "*")
		for path in glob.glob(dirname):
			if os.path.isfile(path):
				yield {"name": unicode(os.path.basename(path), 'utf-8'), "has_subdirs": False}
		return

	def subdirs(self, subdir):
		"""Get a list of subdirs of subdir *subdir* (root is "")
		Each dir is a dict with at least a property 'name'.
		
		Note: Git support in submin only returns branches, and only when
		      requesting subdirs for the root ("")
		"""
		if str(subdir) == "":
			return self.branches()
		return [] # not supported for git

	def remove(self):
		"""Removes repository *name*"""
		if not self.dir.absolute:
			raise Exception("Error, repository path is relative, this should be fixed")

		if not self.dir.exists():
			raise Exception("Repository %s does not exist." % self.name)

		try:
			remote.execute("remove %s" % self.name)
		except remote.NonZeroExitStatus as e:
			raise PermissionError(
				"External command 'remove %s' failed: %s" % \
						(self.name, e))

	def enableCommitEmails(self, enable):
		"""Enables sending of commit messages if *enable* is True."""
		if enable:
			enable_str = "enable"
		else:
			enable_str = "disable"

		remote.execute("commit-email-hook %s %s" % (enable_str, self.name))

	def commitEmailsEnabled(self):
		"""Returns True if sending of commit messages is enabled."""
		hookdir = directory(self.name) + 'hooks'
		hook = hookdir + 'post-receive.d' + '001-commit-email.hook'
		old_hook = hookdir + 'post-receive'
		return os.path.exists(hook) or (
			os.path.exists(old_hook) and
			not shellscript.hasSignature(old_hook, hook_signature))

	def enableTracCommitHook(self, enable):
		if enable:
			enable_str = "enable"
		else:
			enable_str = "disable"

		remote.execute("trac-sync-hook %s %s" % (enable_str, self.name))

	def tracCommitHookEnabled(self):
		"""Returns True if trac sync is enabled."""
		hookdir = directory(self.name) + 'hooks'
		hook = hookdir + 'post-receive.d' + '002-trac-sync.hook'
		return os.path.exists(hook)

	def __str__(self):
		return self.name
