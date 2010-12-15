import codecs

from submin.models import options
from submin.models import group
from repository import list as list_repos
from submin.models.permissions import Permissions
from submin.models.user import FakeAdminUser

def export_authz(**args):
	"""Export authorization/authentication info"""

	authz_filename = options.env_path("svn_authz_file")
	authz = codecs.open(str(authz_filename), "w+", "utf-8")

	# Write all groups
	authz.write("[groups]\n")
	for groupname in group.list(FakeAdminUser()):
		g = group.Group(groupname)
		authz.write("%s = %s\n" % (groupname, ', '.join(g.members())))
	authz.write("\n")

	# Write all repositories and their permissions
	for repository in list_repos():
		if repository["status"] != "ok":
			continue

		perms = Permissions()

		for path in perms.list_paths(repository["name"], "svn"):
			authz.write("[%s:%s]\n" % (repository["name"], path))

			for perm in perms.list_permissions(repository["name"], "svn",
					path):
				if perm["type"] == "group":
					authz.write("@")
				authz.write("%s = %s\n" % (perm["name"], perm["permission"]))
			authz.write("\n")

	authz.close()

def export_notifications(**args):
	"""Export a mailer.py config file
	For each user/repository pair, a config group is created. Only if a user
	has read or read/write permission to one or multiple paths in that
	repository, _and_ if the user has notifications enabled for that
	repository, _and_ if the user has a non-empty email-address. Multiple
	paths are grouped together by a regexp group (multiple|paths)"""
	bindir = options.static_path("hooks") + 'svn'
	
	# get a list of all users
	from submin.models import user
	users = [user.User(name) for name in user.list(user.FakeAdminUser())]

	from submin.models.permissions import Permissions
	p = Permissions()
	groups = []
	for u in users:
		if not u.email:
			continue

		u_notif = u.notifications()

		for repos in u_notif:
			repos_path = str(options.env_path("svn_dir") + repos)
			if not u_notif[repos]["enabled"]:
				continue

			# strip leading /
			paths = [x[1:] for x in p.list_readable_user_paths(repos, "svn", u)]
			if len(paths) == 0:
				continue
			elif len(paths) == 1:
				for_paths = paths[0]
			elif len(paths) > 0:
				for_paths = "(" + "|".join(paths) + ")"

			g = {"for_repos": repos, "repos_path": repos_path, "email": u.email,
				"for_paths": for_paths, "username": u.name}
			groups.append(g)

	templatevariables = {"groups": groups}

	from submin.template.shortcuts import evaluate
	content = evaluate("plugins/vcs/svn/mailer.conf", templatevariables)
	filename = str((options.env_path() + 'conf') + 'mailer.py.conf')
	file(filename, 'w').writelines(content.encode('utf-8'))
