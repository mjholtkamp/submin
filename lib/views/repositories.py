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

		if len(path) < 1:
			return ErrorResponse('Invalid path', request=req)

		if path[0] == 'show':
			return self.show(req, path[1:])

		if path[0] == 'add':
			return self.add(req, path[1:])

		return ErrorResponse('Unknown path', request=req)

	def show(self, req, path):
		localvars = {}

		try:
			repository = Repository(path[0])
		except (IndexError, Repository.DoesNotExist):
			return ErrorResponse('This repository does not exist.', request=req)

		localvars['repository'] = repository
		formatted = evaluate_main('repositories', localvars, request=req)
		return Response(formatted)

	def add(self, req, path):
		config = Config()
		media_url = config.get('www', 'media_url').rstrip('/')

		if req.post and req.post['repository']:
			repository = req.post['repository'].value.strip()
			url = media_url + '/repositories/show/' + repository

			return ErrorResponse('not yet implemented, would otherwise redirect to %s' % url, request=req)

		localvars = {}
		formatted = evaluate_main('newrepository', localvars, request=req)
		return Response(formatted)

	def ajaxhandler(self, req, path):
		repositoryname = ''

		if len(path) > 0:
			repositoryname = path[0]

		return XMLStatusResponse(False, 'operations for repositories are not yet implemented')

