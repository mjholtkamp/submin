#!/usr/bin/python

def buildNotifications(users):
	notifications = {}
	for user in users:
		u_notif = user.notifications()
		if not u_notif:
			continue
		for repo in u_notif:
			if not u_notif[repo]["enabled"]:
				continue

			if not notifications.has_key(repo):
				notifications[repo] = []

			# check if user has email, if not, ignore
			if user.email:
				notifications[repo].append(user.email)
	return notifications

def main():
	from sys import argv, path
	import os
	path.append('_SUBMIN_LIB_DIR_')
	interpreter = "perl"
	scriptname = 'commit-email.pl'
	scriptdir = os.path.dirname(argv[0])
	env = 'SUBMIN_LIB_DIR'
	if env in os.environ:
		path.append(os.environ[env])

	if len(argv) < 4:
		print "Usage: %s <configfile> <repository path> <revision>" % argv[0]
		return

	os.environ['SUBMIN_ENV'] = argv[1]
	repospath = argv[2]
	rev = argv[3]

	from submin.models import backend
	backend.open()

	from submin.models.options import Options
	opts = Options()
	bindir = opts.static_path("hooks") + 'svn'

	from submin.models.user import User, FakeAdminUser
	userlist = [User(name) for name in User.list(FakeAdminUser())]

	n = buildNotifications(userlist)
	repos = os.path.basename(repospath)
	if not n.has_key(repos):
		print "no such repository"
		return

	mailer = bindir + scriptname
	for email in  n[repos]:
		os.system("%s %s '%s' '%s' -s '[%s]' '%s'" % (interpreter, mailer, repospath, rev, repos, email))

if __name__ == "__main__":
	main()
