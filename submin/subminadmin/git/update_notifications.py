from submin.models import repository
from submin.models import user
from submin.models import options
from common import set_git_config, SetGitConfigError

class UpdateFailed(Exception):
	pass

def run(reposname):
	failed, succeeded = [], []
	errors = []
	if reposname:
		repositories = [reposname]
	else:
		# even though we might know the username, it we can't filter on
		# username, as permissions might be revoked from a repository
		# and it won't show up if we use Repositor.list() (because it is
		# revoked). So regenerate for all repositories
		repositories = [x['name'] for x in repository.Repository.list_all() if x['vcs'] == 'git']
	
	# get a list of all users + their notifications as tuples: (u, n)
	# We get the notifications straight away, otherwise we have to
	# call it user * repositories times, and the u.notifications()
	# function can be heavy on the database if called that many times
	# (for a couple of users and 36 repositories, database was hit
	# almost 3000 times during profiling)
	user_notifications = []
	for name in user.list(user.FakeAdminUser()):
		u = user.User(name)
		if not u.email:
			# user without emails cannot be notified
			continue

		n = u.notifications()
		user_notifications.append((u, n))

	for reposname in repositories:
		try:
			update_notification(reposname, user_notifications)
		except SetGitConfigError, e:
			errors.append(str(e))
			failed.append(reposname)
		else:
			succeeded.append(reposname)

	if len(failed) > 0:
		total = len(failed) + len(succeeded)
		msg = "Some repositories failed to update: %s. (%s/%s)" % (
			','.join(failed), len(failed), total)
		raise UpdateFailed(msg)

def update_notification(reposname, user_notifications):
	if not reposname.endswith('.git'):
		reposname += '.git'

	emails = []
	for u_n in user_notifications:
		u, u_notif = u_n
		if reposname in u_notif:
			if u_notif[reposname]['enabled']:
				emails.append(u.email)

	# make unique
	emails = set(emails)

	# set git config
	cfg = options.env_path() + 'git' + reposname + 'config'

	if len(emails) > 0:
		val = ','.join(emails)
	else:
		val = None

	set_git_config(cfg, 'multimailhook.mailinglist', val)
