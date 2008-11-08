#!/usr/bin/python

def buildNotifications(users):
	notifications = {}
	for user in users.itervalues():
		if not user.has_key('notifications_enabled'):
			continue
		for path in [x.strip() for x in user['notifications_enabled'].split(',')]:
			if not notifications.has_key(path):
				notifications[path] = []
			notifications[path].append(user['email'])
	return notifications

def main():
	from sys import argv, path
	import os
	path.append('_SUBMIN_LIB_DIR_')
	scriptname = 'commit-email.pl'
	scriptdir = os.path.dirname(argv[0])
	env = 'SUBMIN_LIB_DIR'
	if env in os.environ:
		path.append(os.environ[env])

	if len(argv) < 4:
		print "Usage: %s <configfile> <repository path> <revision>" % argv[0]
		return

	repospath = argv[2]
	rev = argv[3]
	os.environ['SUBMIN_CONF'] = argv[1]

	try:
		from config.config import Config
	except ImportError, e:
		print e
		print "is environment %s set?" % env
		return

	config = Config()
	bindir = config.get('backend', 'bindir')
	a = config.authz
	n = buildNotifications(a.users())
	repos = os.path.basename(repospath)
	if not n.has_key(repos):
		print "no such repository"
		return

	mailer = os.path.join(bindir, scriptname)
	for email in  n[repos]:
		os.system("%s '%s' '%s' '%s'" % (mailer, repospath, rev, email))

if __name__ == "__main__":
	main()
