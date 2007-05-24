from template import markup

from dispatch.response import Response

class UserGroups(object):
	def handler(self, req, path, ajax=False):
		if ajax:
			return Response('ajax')
		f = open('../templates/usergroups')
		template = ''.join(f.readlines())
		localvars = {}
		users = ["'sabre2th', 'x@elfstone.nl'", "'avaeq', 'x@webdevel.nl'"]
		users.append("'will', 'x@elizeo.nl'")
		users.append("'tux', 'x@lirama.net'")
		users.append("'jan', 'me@jan.net'")
		users.append("'piet', 'ik@janpieter.net'")
		groups = ["'submerge', ['sabre2th', 'avaeq']"]
		groups.append("'willmerge', ['will']")
		localvars['users'] = users
		localvars['groups'] = groups
		formatted = markup(template, None, localvars)
		return Response(formatted)
