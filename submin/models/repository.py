import os
from submin import models
from submin.models import options
from submin.models import permissions
from submin.hooks.common import trigger_hook
from submin.models.trac import Trac, UnknownTrac

class DoesNotExistError(Exception):
	pass
class PermissionError(Exception):
	pass
class VersionError(Exception):
	pass
class VCSImportError(Exception):
	pass

def _vcs_display_name(vcs_type):
	return models.vcs.get(vcs_type, "repository").display_name

def vcs_list():
	return [x.strip() for x in options.value('vcs_plugins').split(',')]

def userHasReadPermissions(username, reposname, vcs):
	perms = permissions.list_by_user(username)
	return _userHasReadPermissions(perms, reposname, vcs)

def _userHasReadPermissions(perms, reposname, vcs):
	for perm in perms:
		name = reposname
		if perm['repository'] != name or perm['vcs'] != vcs:
			continue
		if perm['permission'] in ('r', 'rw'):
			return True
	return False

def url(vcs_type, reposname):
	return models.vcs.get(vcs_type, "repository").url(reposname)

def directory(vcs_type, reposname):
	return models.vcs.get(vcs_type, "repository").directory(reposname)


class Repository(object):
	@staticmethod
	def list_all():
		repositories = []
		for system in vcs_list():
			vcs = models.vcs.get(system, "repository")
			vcs_repos = vcs.list()
			for r in vcs_repos:
				r.update({"vcs": system})
			repositories += vcs_repos

		return repositories

	@staticmethod
	def list(session_user):
		repositories = Repository.list_all()

		if session_user.is_admin:
			return repositories

		filtered = []
		# because we iterate multiple times over perms, make it into a list, otherwise
		# it will be empty after the first time
		perms = list(permissions.list_by_user(session_user.name))
		for repository in repositories:
			name = repository['name']
			status = repository['status']
			vcs = repository['vcs']
			if _userHasReadPermissions(perms, name, vcs):
				filtered.append({"name": name, "status": status, "vcs": vcs})

		return filtered

	@staticmethod
	def add(vcs_type, name, session_user):
		vcs = models.vcs.get(vcs_type, "repository")
		vcs.add(name)
		trigger_hook('repository-create', admin_username=session_user,
			repositoryname=name, vcs_type=vcs_type)

	def __init__(self, repositoryname, vcs_type):
		self.name = repositoryname
		self.vcs_type = vcs_type

		vcs = models.vcs.get(vcs_type, "repository")
		self.repository = vcs.Repository(repositoryname)

		if hasattr(self.repository, "name"):
			self.name = self.repository.name

	def vcs_display_name(self):
		return _vcs_display_name(self.vcs_type)

	def url(self):
		return url(self.vcs_type, self.name)

	def remove(self):
		"""Removes a Repository from disk (NO UNDO)"""
		self.repository.remove()
		trigger_hook('repository-delete', repositoryname=self.name,
				vcs_type=self.vcs_type)

	def subdirs(self, subdir):
		return self.repository.subdirs(subdir)

	def enableCommitEmails(self, enable):
		"""Enables sending of commit messages if *enable* is True."""
		self.repository.enableCommitEmails(enable)

		trigger_hook('repository-notifications-update', 
				repositoryname=self.name, vcs_type=self.vcs_type)

	def enableTracCommitHook(self, enable):
		# only enable when trac env could be found, but always disable (whether trac
		# env could be found or not) (ticket #194, #269)
		if options.value('enabled_trac', 'no') == 'no':
			enable = False

		if enable:
			try:
				trac = Trac(self.name)
			except UnknownTrac:
				enable = False

		self.repository.enableTracCommitHook(enable)

		trigger_hook('repository-notifications-update',
				repositoryname=self.name, vcs_type=self.vcs_type)

	def commitEmailsEnabled(self):
		return self.repository.commitEmailsEnabled()

	def tracCommitHookEnabled(self):
		return self.repository.tracCommitHookEnabled()

__doc__ = """
VCS contract
================

Repository takes care of creating/deleting/listing repositories as well
as some secondary tasks.

* display_name
	The human-readable name of the vcs type

* list()
	Returns a list of repositories

* add(name)
	Create a new repository with name *name*

* url(repo)
	Returns the URL where repository *repo* can be reached (using their own
	method).

* directory(repo)
	Returns the directory where repository *repo* can be found on disk.

* repo.remove(name)
	Removes repository *repo*

* repo.subdirs(subdir)
	Get a list of subdirs of subdir *subdir* (root is "")
	Each dir is a dict with at least a property 'name'.

* repo.enableCommitEmails(enable)
	Enables sending of commit messages if *enable* is True.

* repo.enableTracCommitHook(enable)
	Enables sending of commit messages if *enable* is True.

* repo.commitEmailsEnabled()
	Returns True if sendinf of commit messages is enabled.

* repo.tracCommitHookEnabled()
	Returns True if sendinf of commit messages is enabled.
"""
