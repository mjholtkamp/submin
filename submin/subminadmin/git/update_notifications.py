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
	
	# get a list of all users
	users = [user.User(name) for name in user.list(user.FakeAdminUser())]

	for reposname in repositories:
		try:
			update_notification(reposname, users)
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

def update_notification(reposname, users):
	if not reposname.endswith('.git'):
		reposname += '.git'

	emails = []
	for u in users:
		if not u.email:
			continue

		u_notif = u.notifications()
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
