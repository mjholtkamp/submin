from submin import models
from submin.hooks.common import trigger_hook
storage = models.storage.get("permissions")

def list_paths(repository, vcs_type):
	return storage.list_paths(repository, vcs_type)

def list_by_path(repos, vcs_type, path):
	return storage.list_permissions(repos, vcs_type, path)

def list_by_user(username):
	return storage.list_permissions_by_user(username)

def list_readable_user_paths(repository, vcs_type, user):
	"""Return a list of paths for this *repository* that the *user* is
	   able to read. The *user* is a User object."""
	return list_user_paths_by_permissions(repository, vcs_type, user, ("rw", "r"))

def list_writeable_user_paths(repository, vcs_type, user):
	"""Return a list of paths for this *repository* that the *user* is
	   able to write. The *user* is a User object."""
	return list_user_paths_by_permissions(repository, vcs_type, user, ("rw"))

def list_user_paths_by_permissions(repository, vcs_type, user, permissions):
	groups = user.member_of()
	user_paths = []
	for path in list_paths(repository, vcs_type):
		for perm in list_by_path(repository, vcs_type, path):
			# due to lazy evaluation, user perms overrule group and 'all'
			if (perm['type'] == 'user' and perm['name'] == user.name) or \
					(perm['type'] == 'group' and perm['name'] in groups) or \
					(perm['type'] == 'all'):
				if perm['permission'] in permissions:
					user_paths.append(path)

	return set(user_paths) # remove double entries

def is_writeable(repository, vcs_type, user, path):
	groups = user.member_of()
	for perm in list_by_path(repository, vcs_type, path):
		# due to lazy evaluation, user perms overrule group and 'all'
		if (perm['type'] == 'user' and perm['name'] == user.name) or \
				(perm['type'] == 'group' and perm['name'] in groups) or \
				(perm['type'] == 'all'):
			if perm['permission'] == 'rw':
				return True
			else:
				return False

	if path == '/': # fall through, so '/' failed, and '/' has no parent
		return False
	parent = '/'.join(path.split('/')[:-1])
	if not parent: # happens when path.split('/')[:-1] == ['']
		parent = '/'
	return is_writeable(repository, vcs_type, user, parent)

def add(repos, repostype, path, subject, subjecttype, perm):
	"""Sets permission for repos:path, raises a
	Repository.DoesNotExistError if repos does not exist."""
	if repos != "":
		from submin.models.repository import Repository
		r = Repository(repos, repostype) # check if exists

	_assert_permission_allowed(repostype, path, perm)

	storage.add_permission(repos, repostype, path, subject, subjecttype,
			perm)
	trigger_hook('permission-update', repositoryname=repos,
			repository_path=path, vcs_type=repostype)

def _assert_permission_allowed(repostype, path, perm):
	if repostype == "git":
		if path != "/" and perm != "w": # only "w"
			raise InvalidPermissionError()
		if path == "/" and perm != "rw" and perm != "r": # only "r, rw"
			raise InvalidPermissionError()

def change(repos, repostype, path,
		subject, subjecttype, perm):
	"""Changes permission for repos:path, raises a
	Repository.DoesNotExistError if repos does not exist."""
	from submin.models.repository import Repository
	r = Repository(repos, repostype) # just for the exception
	_assert_permission_allowed(repostype, path, perm)
	storage.change_permission(repos, repostype, path, subject, subjecttype,
			perm)
	trigger_hook('permission-update', repositoryname=repos,
			repository_path=path, vcs_type=repostype)

def remove(repos, repostype, path, subject, subjecttype):
	storage.remove_permission(repos, repostype, path, subject, subjecttype)
	trigger_hook('permission-update', repositoryname=repos,
			repository_path=path, vcs_type=repostype)

__doc__ = """
Storage Contract
================

* list_paths(repos)
	Returns an array of paths (strings) that have permissions set.

* list_permissions(repos, repostype, path)
	Returns a list of permissions of *path* in *repos*. Each permission is
	in the following form:
		{'name': 'testUser', 'type': 'user', 'permission': 'rw'}

* list_permissions_by_user(username)
	Get all permissions for a specific user, including permissions that groups have that
	this user is a member of.

* add_permission(repos, repostype, path, subject, subjecttype, perm)
	Set the permission of *repos*:*path* to *subject* (user, group, all)
	to *perm*. If the *subjecttype* is 'all', then an anonymous user is
	assumed.

* change_permission(repos, repostype, path, subject, subjecttype, perm)
	Change the permission of *repos*:*path* with *subject* and type
	*subjecttype* to *perm*.

* remove_permission(repos, repostype, path, subject, subjecttype)
	Removes the permission from *repos*:*path* for *subject* with type
	*subjecttype*

"""
