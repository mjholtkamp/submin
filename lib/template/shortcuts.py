from config.config import Config
from __init__ import evaluate
from models.user import User
from models.group import Group

def evaluate_main(templatename, templatevariables={}):
	templatevariables['main_include'] = templatename

	config = Config()

	users = []
	htpasswd_users = config.htpasswd.users()
	htpasswd_users.sort()
	for user in htpasswd_users:
		try:
			users.append(User(config, user))
		except User.DoesNotExist:
			pass

	groups = []
	authz_groups = config.authz.groups()
	authz_groups.sort()
	for group in authz_groups:
		groups.append(Group(config, group))

	templatevariables['main_users'] = users
	templatevariables['main_groups'] = groups

	templatevariables['main_media_url'] = config.get('www', 'media_url').rstrip('/')


	return evaluate('../templates/main', templatevariables)
