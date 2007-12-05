from template.shortcuts import evaluate_main
from dispatch.response import Response
from dispatch.response import HTTP500
from config.config import Config
from models.user import User
from models.group import Group
from models.repository import Repository

class Repositories(object):
	def handler(self, req, path, ajax=False):
		if ajax:
			return self.ajaxhandler(req, path)

		config = Config()

		localvars = {}

		try:
			repository = Repository(config, path[0])
		except (IndexError, Repository.DoesNotExist):
			return Response('Woops, repository does not exist!')

		localvars['repository'] = repository
		formatted = evaluate_main('repositories', localvars)
		return Response(formatted)

	def ajaxhandler(self, req, path):
		config = Config()

		success = False
		error = ''
		response = None
		repositoryname = ''

		if len(path) > 0:
			repositoryname = path[0]

		error = 'operations for repositories are not yet implemented'

		if success:
			response = Response('Success!')
		else:
			response = HTTP500(error)

		return response
