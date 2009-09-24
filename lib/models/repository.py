import os
import models
systems = models.vcs.list()

class DoesNotExistError(Exception):
	pass
class PermissionError(Exception):
	pass
class VersionError(Exception):
	pass
class VCSImportError(Exception):
	pass

class Repository(object):
	@staticmethod
	def list_all():
		repositories = []
		for system in systems:
			backend = models.vcs.get(system, "repository")
			repositories += backend.list()

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
					filtered.append({"name": name, "status": status})
			repositories = filtered

		return repositories

	@staticmethod
	def list_vcs():
		return systems

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
	def add(system, name):
		backend = models.vcs.get(system, "repository")
		backend.add(name)

	def __init__(self, repositoryname):
		self.name = repositoryname
		self._type = 'repository'

		for system in systems:
			backend = models.vcs.get(system, "repository")
			try:
				self._repository = backend.Repository(repositoryname)
				return # we found one, no need to check other systems
			except DoesNotExistError:
				pass

		raise DoesNotExistError

	def remove(self):
		"""Removes a Repository from disk (NO UNDO)"""
		self._repository.remove()

	def subdirs(self, subdir):
		return self._repository.subdirs(subdir)

	def enableCommitEmails(self, enable):
		"""Enables sending of commit messages if *enable* is True."""
		self._repository.enableCommitEmails(enable)

	def commitEmailsEnabled(self):
		return self._repository.commitEmailsEnabled()

__doc__ = """
Backend contract
================

Repository takes care of creating/deleting/listing repositories as well
as some secondary tasks.

* list()
	Returns a list of repositories

* add(name)
	Create a new repository with name *name*

* remove(name)
	Removes repository *name*

* subdirs(subdir)
	Get a list of subdirs of subdir *subdir* (root is "")
	Each dir is a dict with at least a property 'name'.

* enableCommitEmails(enable)
	Enables sending of commit messages if *enable* is True.

* commitEmailsEnabled()
	Returns True if sendinf of commit messages is enabled.
"""
