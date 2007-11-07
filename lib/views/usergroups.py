from template import evaluate
from models.user import User
from models.group import Group
from authz.authz import Authz
from authz.htpasswd import HTPasswd
from dispatch.response import Response
from config.config import Config

class UserGroups(object):
	def handler(self, req, path, ajax=False):
		if ajax:
			return Response('ajax')

		config = Config()

		authz = Authz(config.get('svn', 'authz_file'))
		htpasswd = HTPasswd(config.get('svn', 'access_file'))

		localvars = {}
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

		localvars['users'] = users
		localvars['groups'] = groups
		formatted = evaluate('../templates/usergroups', localvars)
		return Response(formatted)
