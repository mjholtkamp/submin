from submin import models
storage = models.storage.get("permissions")

from submin.models.repository import Repository

class Permissions(object):
	def list_paths(self, repository):
		return storage.list_paths(repository)

	def list_permissions(self, repos, path):
		return storage.list_permissions(repos, path)

	def list_readable_user_paths(self, repository, user):
		"""Return a list of paths for this *repository* that the *user* is
		   able to read. The *user* is a User object."""
		groups = user.member_of()
		user_paths = []
		for path in self.list_paths(repository):
			for perm in self.list_permissions(repository, path):
				# due to lazy evaluation, user perms overrule group and 'all'
				if (perm['type'] == 'user' and perm['name'] == user.name) or \
						(perm['type'] == 'group' and perm['name'] in groups) or \
						(perm['type'] == 'all'):
					if perm['permission'] in ['r', 'rw']:
						user_paths.append(path)

		return set(user_paths) # remove double entries

	def add_permission(self, repos, repostype, path,
			subject, subjecttype, perm):
		"""Sets permission for repos:path, raises a
		Repository.DoesNotExistError if repos does not exist."""
		if repos != "":
			r = Repository(repos) # check if exists

		storage.add_permission(repos, path, subject, subjecttype, perm)
		models.vcs.export_auth_repository(repostype)

	def change_permission(self, repos, repostype, path,
			subject, subjecttype, perm):
		"""Changes permission for repos:path, raises a
		Repository.DoesNotExistError if repos does not exist."""
		r = Repository(repos) # just for the exception
		storage.change_permission(repos, path, subject, subjecttype, perm)
		models.vcs.export_auth_repository(repostype)

	def remove_permission(self, repos, repostype, path, subject, subjecttype):
		storage.remove_permission(repos, path, subject, subjecttype)
		models.vcs.export_auth_repository(repostype)

__doc__ = """
Storage Contract
================

* list_paths(repos)
	Returns an array of paths (strings) that have permissions set.

* list_permissions(repos, path)
	Returns a list of permissions of *path* in *repos*. Each permission is
	in the following form:
		{'name': 'testUser', 'type': 'user', 'permission': 'rw'}

* add_permission(repos, path, subject, subjecttype, perm)
	Set the permission of *repos*:*path* to *subject* (user, group, all)
	to *perm*. If the *subjecttype* is 'all', then an anonymous user is
	assumed.

* change_permission(repos, path, subject, subjecttype, perm)
	Change the permission of *repos*:*path* with *subject* and type
	*subjecttype* to *perm*.

* remove_permission(repos, path, subject, subjecttype)
	Removes the permission from *repos*:*path* for *subject* with type
	*subjecttype*

"""
