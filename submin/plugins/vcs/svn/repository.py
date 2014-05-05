# -*- coding: utf-8 -*-
import os
import commands
import exceptions

from submin.path.path import Path
from submin.unicode import uc_str, uc_to_svn, uc_from_svn
from submin.common import shellscript
from submin.models import options
from submin.models.exceptions import UnknownKeyError, MissingConfig
from submin.models.repository import DoesNotExistError, PermissionError, VersionError, VCSImportError

from export import export_notifications

display_name = "Subversion"
has_path_permissions = True

def list():
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
		except VersionError:
			status = "wrong version"

		repositories.append({"name": repos, "status": status})

	return repositories

def _repositoriesOnDisk():
	"""Returns all repositories that are found on disk"""
	import glob, os.path
	reposdir = options.env_path('svn_dir')
	reps = glob.glob(str(reposdir + '*'))
	repositories = []
	for rep in reps:
		if os.path.isdir(rep):
			repositories.append(rep[rep.rfind('/') + 1:])

	return repositories

def add(name):
	reposdir = options.env_path('svn_dir')
	newrepos = reposdir + name
	path = options.value('env_path', "/bin:/usr/bin:/usr/local/bin:/opt/local/bin")
	cmd = "PATH='%s' svnadmin create '%s'" % (path, str(newrepos))
	(exitstatus, outtext) = commands.getstatusoutput(cmd)
	if exitstatus != 0:
		raise PermissionError("External command 'svnadmin' failed: %s" % outtext)

	repos = Repository(name)
#	repos.changeNotifications(True)

def url(reposname):
	try:
		return str(options.url_path('base_url_svn') + reposname)
	except UnknownKeyError as e:
		raise MissingConfig('Please make sure base_url_svn is set in config')

def directory(reposname):
	# FIXME: encoding?
	base_dir = options.env_path('svn_dir')
	reposdir = base_dir + reposname
	# We could use realpath to check, but we don't want to prevent usage of
	# symlinks in their svn directory
	if not os.path.normpath(reposdir).startswith(os.path.normpath(base_dir)):
		raise Exception('Subversion directory outside base path');

	return reposdir


class Repository(object):
	"""Internally, this class uses unicode to represent files and directories.
It is converted to UTF-8 (or other?) somewhere in the dispatcher."""

	def __init__(self, name):
		try:
			global fs, repos, core, SubversionException
			from svn import fs, repos, core
			from svn.core import SubversionException
		except ImportError:
			raise VCSImportError("Failed to import python 'svn' module, please install")

		self.name = name
		self.svn_signature = "### SUBMIN AUTOCONFIG, DO NOT ALTER FOLLOWING LINE ###\n"
		self.trac_signature = "### SUBMIN TRAC AUTOCONFIG, DO NOT ALTER FOLLOWING LINE ###\n"

		reposdir = options.env_path('svn_dir')

		self.initialized = False
		self.dirs = self.subdirs("")
		self.initialized = True

	def subdirs(self, path):
		'''Return subdirs (not recursive) of 'path' relative to our reposdir
		Subdirs are returned as a hash with two entities: 'name' and 
		'has_subdirs', which should be self-explanatory.'''

		files = self.get_entries(path)
		dirs = []
		for f in files:
			if f['kind'] == 'dir':
				hassubdirs = self.hassubdirs(os.path.join(path, f['name']))
				entry = {}
				entry['name'] = f['name']
				entry['has_subdirs'] = hassubdirs
				dirs.append(entry)

		dirs.sort(lambda a, b: cmp(unicode.lower(a['name']), unicode.lower(b['name'])))
		return dirs

	def get_entries(self, path):
		# lots of conversions from and to utf-8
		disk_url = directory(self.name)
		root_path_utf8 = repos.svn_repos_find_root_path(disk_url)
		if root_path_utf8 is None or not os.path.exists(root_path_utf8):
			raise DoesNotExistError(disk_url)

		try:
			repository = repos.svn_repos_open(root_path_utf8)
		except SubversionException as e:
			# check for messages like the following:
			# "Expected FS Format 'x'; found format 'y'"
			# there are different errorcodes for each version, so do a string
			# match instead of errorcode match
			errstr = str(e)
			if "Expected" in errstr and "format" in errstr and "found" in errstr:
				raise VersionError

			raise PermissionError

		fs_ptr = repos.svn_repos_fs(repository)

		path_utf8 = uc_to_svn(uc_str(path))
		youngest_revision_number = fs.youngest_rev(fs_ptr)
		try:
			root = fs.revision_root(fs_ptr, youngest_revision_number)
		except SubversionException as e:
			raise PermissionError

		entries = fs.dir_entries(root, path_utf8)

		dirs = []
		for entry in entries.keys():
			d = {}
			node_type = fs.check_path(root, os.path.join(path_utf8, entry))
			if (node_type == core.svn_node_dir):
				d['kind'] = 'dir'
			elif (node_type == core.svn_node_file):
				d['kind'] = 'file'
			else:
				d['kind'] = 'unknown'
			d['name'] = uc_from_svn(entry)
			dirs.append(d)

		return dirs

	def hassubdirs(self, path):
		import os

		files = self.get_entries(path)
		for f in files:
			if f['kind'] == 'dir':
				return True # only one is enough

		return False

	def commitEmailsEnabled(self):
		reposdir = options.env_path('svn_dir')
		hook = reposdir + self.name + 'hooks' + 'post-commit'
		return shellscript.hasSignature(str(hook), self.svn_signature)

	def tracCommitHookEnabled(self):
		reposdir = options.env_path('svn_dir')
		hook = reposdir + self.name + 'hooks' + 'post-commit'
		return shellscript.hasSignature(str(hook), self.trac_signature)

	def enableCommitEmails(self, enable):
		"""Add or remove our script to/from the post-commit hook"""
		import os

		bindir = options.static_path('hooks') + 'svn'
		fullpath = str(bindir + 'mailer.py')
		base_env = options.env_path()
		mailer_conf = str((base_env + 'conf') + 'mailer.py.conf')

		if not os.path.exists(mailer_conf):
			export_notifications() # create mailer_conf

		new_hook = '/usr/bin/python %s commit "$1" "$2" "%s"\n' % \
				(fullpath, mailer_conf)

		self.rewritePostCommitHook(self.svn_signature, new_hook, enable)

	def enableTracCommitHook(self, enable):
		"""Add or remove trac commit script to/from the post-commit hook"""
		import os

		bindir = options.static_path('hooks') + 'svn'
		fullpath = str(bindir + 'trac-post-commit-hook')
		trac_env = str(options.env_path('trac_dir') + self.name)

		new_hook = '/usr/bin/python %s -p %s -r "$2"\n' % \
				(fullpath, trac_env)

		self.rewritePostCommitHook(self.trac_signature, new_hook, enable)

	def rewritePostCommitHook(self, signature, new_hook, enable):
		reposdir = options.env_path('svn_dir')
		hook = reposdir + self.name + 'hooks' + 'post-commit'

		shellscript.rewriteWithSignature(hook, signature, new_hook, enable, mode=0o755)

	def remove(self):
		reposdir = options.env_path('svn_dir')
		newrepos = reposdir + self.name
		if not newrepos.absolute:
			raise Exception("Error, repository path is relative, this should be fixed")

		cmd = 'rm -rf "%s"' % newrepos
		(exitstatus, outtext) = commands.getstatusoutput(cmd)
		if exitstatus != 0:
			raise Exception("could not remove repository %s" % self.name)

	def __str__(self):
		return self.name
