from template import markup

from dispatch.response import Response

class UserGroups(object):
	def handler(self, req, path, ajax=False):
		if ajax:
			return Response('ajax')
		f = open('../templates/usergroups')
		template = ''.join(f.readlines())
		formatted = markup(template)
		return Response(formatted)
