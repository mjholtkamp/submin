from template import evaluate
from models.user import User
from models.group import Group

from dispatch.response import Response

class UserGroups(object):
	def handler(self, req, path, ajax=False):
		if ajax:
			return Response('ajax')
		# f = open('../templates/usergroups')
		# template = ''.join(f.readlines())
		localvars = {}
		users = [User('sabre2th', 'x@elfstone.nl'), User('avaeq', 'x@webdevel.nl')]
		users.append(User('will', 'x@elizeo.nl'))
		users.append(User('tux', 'x@lirama.net'))
		users.append(User('jan', 'me@jan.net'))
		users.append(User('piet', 'ik@janpieter.net'))
		groups = [Group('submerge', ['sabre2th', 'avaeq'])]
		groups.append(Group('willmerge', ['will']))
		localvars['users'] = users
		localvars['groups'] = groups
		formatted = evaluate('../templates/usergroups', localvars)
		return Response(formatted)
