from template.shortcuts import evaluate_main
from dispatch.response import Response, XMLStatusResponse, XMLTemplateResponse, Redirect
from views.error import ErrorResponse
from dispatch.view import View
from models.user import User
from models.group import Group
from models.repository import Repository
from auth.decorators import *

class Repositories(View):
	@login_required
	def handler(self, req, path):
		localvars = {}

		if req.is_ajax():
			return self.ajaxhandler(req, path)

		if len(path) < 1:
			return ErrorResponse('Invalid path', request=req)

		if len(path) > 0:
			localvars['selected_type'] = 'repositories'
		if len(path) > 1:
			localvars['selected_object'] = path[1]

		if path[0] == 'show':
			return self.show(req, path[1:], localvars)

		if path[0] == 'add':
			return self.add(req, path[1:], localvars)

		return ErrorResponse('Unknown path', request=req)

	def show(self, req, path, localvars):
		try:
			repository = Repository(path[0])
		except (IndexError, Repository.DoesNotExist):
			return ErrorResponse('This repository does not exist.', request=req)

		localvars['repository'] = repository
		formatted = evaluate_main('repositories.html', localvars, request=req)
		return Response(formatted)

	def add(self, req, path, localvars):
		config = Config()
		media_url = config.get('www', 'media_url').rstrip('/')

		if req.post and req.post['repository']:
			import re

			repository = req.post['repository'].value.strip()
			if re.findall('[^a-zA-Z0-9_]', repository):
				return ErrorResponse('Invalid characters in repository name', request=req)

			url = media_url + '/repositories/show/' + repository

			reposdir = config.get('svn', 'repositories')
			newrepos = reposdir + '/' + repository
			if os.system('svnadmin create %s' % newrepos) == 0:
				return Redirect(url)

			return ErrorResponse('could not create repository', request=req)

		formatted = evaluate_main('newrepository.html', localvars, request=req)
		return Response(formatted)

	def getsubdirs(self, req, repositoryname):
		try:
			repository = Repository(repositoryname)
		except (IndexError, Repository.DoesNotExist):
			return ErrorResponse('This repository does not exist.', request=req)

		svn_path = req.post['getsubdirs'].value.strip('/')
		dirs = repository.getsubdirs(svn_path)
		templatevars = {'dirs': dirs}
		return XMLTemplateResponse('ajax/repositorytree.xml', templatevars)

	def getpermissions(self, req, repositoryname):
		config = Config()
		try:
			repository = Repository(repositoryname)
		except (IndexError, Repository.DoesNotExist):
			return ErrorResponse('This repository does not exist.', request=req)

		svn_path = req.post['getpermissions'].value.rstrip('/')
		if not svn_path.startswith('/'):
			svn_path = '/' + svn_path

		perms = []
		authz_paths = [x[1] for x in repository.authz_paths]
		if svn_path in authz_paths:
			perms = config.authz.permissions(repositoryname, svn_path)

		templatevars = {'perms': perms, 'repository': repositoryname, 'path': svn_path}
		return XMLTemplateResponse('ajax/repositoryperms.xml', templatevars)

	def getpermissionpaths(self, req, repositoryname):
		config = Config()
		try:
			repository = Repository(repositoryname)
		except (IndexError, Repository.DoesNotExist):
			return ErrorResponse('This repository does not exist.', request=req)

		authz_paths = [x[1] for x in repository.authz_paths]
		templatevars = {'repository': repositoryname, 'paths': authz_paths}
		return XMLTemplateResponse('ajax/repositorypermpaths.xml', templatevars)

	def ajaxhandler(self, req, path):
		repositoryname = ''

		if len(path) < 2:
			return XMLStatusResponse(False, 'Invalid path')

		action = path[0]
		repositoryname = path[1]

		if 'getsubdirs' in req.post:
			return self.getsubdirs(req, repositoryname)

		if 'getpermissions' in req.post:
			return self.getpermissions(req, repositoryname)

		if 'getpermissionpaths' in req.post:
			return self.getpermissionpaths(req, repositoryname)

		return XMLStatusResponse(False, 'operations for repositories are not yet implemented')

