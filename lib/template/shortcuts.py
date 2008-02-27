from config.config import Config
from __init__ import evaluate
from models.user import User
from models.group import Group
from models.repository import Repository

def evaluate_main(templatename, templatevariables={}, request=None):
	templatevariables['main_include'] = templatename

	config = Config()

	is_admin = False
	session_user = None
	if request and 'user' in request.session:
		try:
			session_user = request.session['user']
			is_admin = session_user.is_admin
		except User.DoesNotExist:
			pass

	users = []
	htpasswd_users = config.htpasswd.users()
	htpasswd_users.sort()
	if is_admin:
		for user in htpasswd_users:
			try:
				users.append(User(user))
			except User.DoesNotExist:
				pass
	else:
		users.append(session_user)

	groups = []
	authz_groups = config.authz.groups()
	authz_groups.sort()

	# make sure submin-admins is in front (it's special!)
	special_group = 'submin-admins'
	if special_group in authz_groups:
		authz_groups.remove(special_group)
		authz_groups.insert(0, special_group)

	for groupname in authz_groups:
		group = Group(groupname)
		if is_admin or session_user.name in group.members:
			groups.append(group)

	repositories = []
	repository_names = config.repositories()

	for repos in repository_names:
		repositories.append(Repository(repos))

	templatevariables['main_users'] = users
	templatevariables['main_groups'] = groups
	templatevariables['main_repositories'] = repositories

	templatevariables['main_media_url'] = config.get('www', 'media_url').rstrip('/')

	if request:
		templatevariables['request'] = request
		if 'user' in request.session:
			templatevariables['main_user'] = request.session['user']

	templatevariables['is_admin'] = is_admin

	return evaluate('main.html', templatevariables)
