import codecs

from submin.models.options import Options
from submin.models.group import Group
from repository import list as list_repos
from submin.models.permissions import Permissions
from submin.models.user import FakeAdminUser

def export_auth(authtype):
	"""Export authorization/authentication info for authtype:
	"user", "group", "repository"."""

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

def export_notifications():
	o = Options()
	bindir = o.static_path("hooks") + 'svn'
	
	# get a list of all users
	from submin.models.user import User, FakeAdminUser
	users = [User(name) for name in User.list(FakeAdminUser())]

	# write a group-section for each user, for each repos, for each path
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

			for_paths = ",".join(p.list_readable_user_paths(repos, user))
			group = {"for_repos": repos, "email": user.email,
				"for_paths": for_paths}
			groups.append(group)

	templatevariables = {"groups": groups}

	from submin.template.shortcuts import evaluate
	content = evaluate("plugins/vcs/svn/mailer.conf", templatevariables)

	print content
