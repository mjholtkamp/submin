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
	def list(session_user):
		repositories = []
		for system in systems:
			backend = models.vcs.get(system, "repository")
			repositories += backend.list(session_user)

		return repositories

	@staticmethod
	def list_vcs():
		return systems

	@staticmethod
	def add(system, name):
		backend = models.vcs.get(system, "repository")
		backend.add(name)

	def __init__(self, repositoryname):
		"""Returns a Repository object"""
		self._name = repositoryname

		for system in systems:
			backend = models.vcs.get(system, "repository")
			try:
				self._repository = backend.Repository(repositoryname)
				break # we found one, no need to check other systems
			except DoesNotExistError:
				pass

	def remove(self):
		"Removes a Repository from disk (NO UNDO)"
		self._repository.remove()

	def subdirs(self, subdir):
		return []

	def userHasReadPermissions(self, session_user):
		if session_user.notifications.has_key(self.name):
			perm = session_user.notifications[self.name]
			if perm['allowed']:
				return True

		return False

	def _getName(self):
		return self._name

	name     = property(_getName)

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

* subdirs(repository, subdir)
	Get a list of subdirs of repository *repository* and subdir *subdir*.
	Each dir is a dict with at least a property 'name'.
"""
