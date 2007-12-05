from config.config import Config
from __init__ import evaluate
from models.user import User
from models.group import Group
from authz.authz import Authz
from authz.htpasswd import HTPasswd

def evaluate_main(templatename, templatevariables={}):
	templatevariables['main_include'] = templatename

	# TODO: split up into models.
	config = Config()

	authz = Authz(config.get('svn', 'authz_file'))
	htpasswd = HTPasswd(config.get('svn', 'access_file'))

	users = []
	authz_users = authz.users()
	htpasswd_users = htpasswd.users()
	htpasswd_users.sort()
	for user in htpasswd_users:
		email = user + '@example.com'
		if authz_users.has_key(user):
			if authz_users[user].has_key('email'):
				email = authz_users[user]['email']
		users.append(User(user, email))

	groups = []
	authz_groups = authz.groups()
	authz_groups.sort()
	for group in authz_groups:
		members = authz.members(group)
		groups.append(Group(group, members))

	templatevariables['main_users'] = users
	templatevariables['main_groups'] = groups

	templatevariables['main_media_url'] = config.get('www', 'media_url').rstrip('/')


	return evaluate('../templates/main', templatevariables)
