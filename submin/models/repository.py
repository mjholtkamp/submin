import os
from submin import models
from submin.models import options
from submin.hooks.common import trigger_hook

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

		if not session_user.is_admin:
			# filter repositories
			filtered = []
			for repository in repositories:
				name = repository['name']
				status = repository['status']
				if Repository.userHasReadPermissions(name, session_user):
					filtered.append({"name": name, "status": status,
						"vcs": repository["vcs"]})
			repositories = filtered

		return repositories

	@staticmethod
	def userHasReadPermissions(reposname, session_user):
		return True # for now, every user is able to set permissions
		# should be replaced by submin_permissions instead of 'notifications'
		if session_user.notifications().has_key(reposname):
			perm = session_user.notifications()[reposname]
			if perm['allowed']:
				return True

		return False

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
			# for example, we may want to add .git to repo.name, and leave the
			# .git part off the display_name
			self.name = self.repository.name

	def vcs_display_name(self):
		return _vcs_display_name(self.vcs_type)

	def display_name(self):
		"""Returns the human-readable name of the repository *repo*"""
		return self.repository.display_name()

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
		if options.value('trac_enable', True):
			self.repository.enableTracEmails(True)

	def commitEmailsEnabled(self):
		return self.repository.commitEmailsEnabled()

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

* repo.display_name()
	Returns the human-readable name of the repository *repo*

* repo.remove(name)
	Removes repository *repo*

* repo.subdirs(subdir)
	Get a list of subdirs of subdir *subdir* (root is "")
	Each dir is a dict with at least a property 'name'.

* repo.enableCommitEmails(enable)
	Enables sending of commit messages if *enable* is True.

* repo.commitEmailsEnabled()
	Returns True if sendinf of commit messages is enabled.
"""
