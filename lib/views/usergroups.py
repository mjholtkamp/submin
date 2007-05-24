from template import markup
from models.user import User

from dispatch.response import Response

class UserGroups(object):
	def handler(self, req, path, ajax=False):
		if ajax:
			return Response('ajax')
		f = open('../templates/usergroups')
		template = ''.join(f.readlines())
		localvars = {}
		users = [User('sabre2th', 'x@elfstone.nl'), User('avaeq', 'x@webdevel.nl')]
		users.append(User('will', 'x@elizeo.nl'))
		users.append(User('tux', 'x@lirama.net'))
		users.append(User('jan', 'me@jan.net'))
		users.append(User('piet', 'ik@janpieter.net'))
		#groups = ["'submerge', ['sabre2th', 'avaeq']"]
		#groups.append("'willmerge', ['will']")
		localvars['users'] = users
		#localvars['groups'] = groups
		formatted = markup(template, None, localvars)
		return Response(formatted)
