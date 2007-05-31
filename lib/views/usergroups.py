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

		for user in htpasswd.users():
			users.append(User(user, user + '@example.com'))

		groups = []
		for group in authz.groups():
			members = authz.members(group)
			groups.append(Group(group, members))

		localvars['users'] = users
		localvars['groups'] = groups
		formatted = evaluate('../templates/usergroups', localvars)
		return Response(formatted)
