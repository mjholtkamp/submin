from models.options import Options
from models.group import Group
from repository import list as list_repos
from models.permissions import Permissions
from models.user import FakeAdminUser

def export_auth(authtype):
	"""Export authorization/authentication info for authtype:
	"user", "group", "repository"."""

	o = Options()
	authz_filename = o.env_path("svn_authz_file")
	authz = open(str(authz_filename), "w+")

	# Write all groups
	authz.write("[groups]\n")
	for groupname in Group.list(FakeAdminUser()):
		group = Group(groupname)
		authz.write("%s = %s\n" % (groupname, ', '.join(group.members())))
	authz.write("\n")

	# Write all repositories and their permissions
	for repository in list_repos():
		print "Exporting authz for", repository["name"]," (status: %s)" % repository["status"]
		if repository["status"] != "ok":
			continue

		perm = Permissions()

		for path in perm.list_paths(repository["name"]):
			authz.write("[%s:%s]\n" % (repository["name"], path))

			for perm in perm.list_permissions(repository["name"], path):
				if perm["type"] == "group":
					authz.write("@")
				authz.write("%s = %s\n" % (perm["name"], perm["permission"]))
			authz.write("\n")

	authz.close()
