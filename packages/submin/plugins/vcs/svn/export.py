import codecs

from submin.models.options import Options
from submin.models.group import Group
from repository import list as list_repos
from submin.models.permissions import Permissions
from submin.models.user import FakeAdminUser

def export_authz(**args):
	"""Export authorization/authentication info"""

	o = Options()
	authz_filename = o.env_path("svn_authz_file")
	authz = codecs.open(str(authz_filename), "w+", "utf-8")

	# Write all groups
	authz.write("[groups]\n")
	for groupname in Group.list(FakeAdminUser()):
		group = Group(groupname)
		authz.write("%s = %s\n" % (groupname, ', '.join(group.members())))
	authz.write("\n")

	# Write all repositories and their permissions
	for repository in list_repos():
		if repository["status"] != "ok":
			continue

		perms = Permissions()

		for path in perms.list_paths(repository["name"]):
			authz.write("[%s:%s]\n" % (repository["name"], path))

			for perm in perms.list_permissions(repository["name"], path):
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
	o = Options()
	bindir = o.static_path("hooks") + 'svn'
	
	# get a list of all users
	from submin.models.user import User, FakeAdminUser
	users = [User(name) for name in User.list(FakeAdminUser())]

	from submin.models.permissions import Permissions
	p = Permissions()
	groups = []
	for user in users:
		if not user.email:
			continue

		u_notif = user.notifications()

		for repos in u_notif:
			if not u_notif[repos]["enabled"]:
				continue

			# strip leading /
			paths = [x[1:] for x in p.list_readable_user_paths(repos, user)]
			if len(paths) == 0:
				continue
			elif len(paths) == 1:
				for_paths = paths[0]
			elif len(paths) > 0:
				for_paths = "(" + "|".join(paths) + ")"

			group = {"for_repos": repos, "email": user.email,
				"for_paths": for_paths, "username": user.name}
			groups.append(group)

	templatevariables = {"groups": groups}

	from submin.template.shortcuts import evaluate
	content = evaluate("plugins/vcs/svn/mailer.conf", templatevariables)

#	raise Exception(content.encode('utf-8'))
