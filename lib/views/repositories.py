from template.shortcuts import evaluate_main
from dispatch.response import Response, XMLStatusResponse
from views.error import ErrorResponse
from dispatch.view import View
from models.user import User
from models.group import Group
from models.repository import Repository
from auth.decorators import *

class Repositories(View):
	@login_required
	def handler(self, req, path):
		if req.is_ajax():
			return self.ajaxhandler(req, path)

		localvars = {}

		try:
			repository = Repository(path[0])
		except (IndexError, Repository.DoesNotExist):
			return ErrorResponse('This repository does not exist.', request=req)

		localvars['repository'] = repository
		formatted = evaluate_main('repositories', localvars, request=req)
		return Response(formatted)

	def ajaxhandler(self, req, path):
		repositoryname = ''

		if len(path) > 0:
			repositoryname = path[0]

		return XMLStatusResponse(False, 'operations for repositories are not yet implemented')

