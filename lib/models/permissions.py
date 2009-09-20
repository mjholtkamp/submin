import models
backend = models.backend.get("permissions")

from models.repository import Repository

class Permissions(object):
	def list_paths(self, repository):
		return backend.list_paths(repository)

	def list_permissions(self, repos, path):
		return backend.list_permissions(repos, path)

	def set_permission(self, repos, path, subject, subjecttype, perm):
		"""Sets permission for repos:path, raises a
		Repository.DoesNotExistError if repos does not exist."""
		r = Repository(repos) # just for the exception
		backend.set_permission(repos, path, subject, subjecttype, perm)

	def remove_permission(self, repos, path, subject, subjecttype):
		backend.remove_permission(repos, path, subject, subjecttype)

__doc__ = """
Backend Contract
================

* list_paths(repos)
	Returns an array of paths (strings) that have permissions set.

* list_permissions(repos, path)
	Returns a list of permissions of *path* in *repos*. Each permission is
	in the following form:
		{'name': 'testUser', 'type': 'user', 'permission': 'rw'}

* set_permission(repos, path, subject, subjecttype, perm)
	Set the permission of repos:path to subject (user, group, all)
	to 'perm'. If the subjecttype is 'all', then an anonymous user is
	assumed.

* remove_permission(repos, path, subject, subjecttype)
	Removes the permission from *repos*:*path* for *subject* with type
	*subjecttype*

"""
