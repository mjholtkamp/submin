from template.shortcuts import evaluate_main
from dispatch.response import Response
from dispatch.response import HTTP500
from config.config import Config
from models.user import User
from models.group import Group

class Groups(object):
	def handler(self, req, path, ajax=False):
		if ajax:
			return self.ajaxhandler(req, path)

		config = Config()

		localvars = {}

		try:
			group = Group(config, path[0])
		except (IndexError, Group.DoesNotExist):
			return Response('Woops, group does not exist!')

		localvars['group'] = group
		formatted = evaluate_main('groups', localvars)
		return Response(formatted)

	def ajaxhandler(self, req, path):
		config = Config()

		success = False
		error = ''
		response = None
		username = ''

		if len(path) > 0:
			groupname = path[0]

		error = 'operations for groups are not yet implemented'

		if success:
			response = Response('Success!')
		else:
			response = HTTP500(error)

		return response
