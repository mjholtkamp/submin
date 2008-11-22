from template.shortcuts import evaluate_main
from dispatch.response import Response, XMLStatusResponse, XMLTemplateResponse, Redirect
from views.error import ErrorResponse
from dispatch.view import View
from models.user import User
from models.group import Group
from models.repository import Repository
from auth.decorators import *
from path.path import Path
from ConfigParser import NoOptionError

class Repositories(View):
	@login_required
	def handler(self, req, path):
		localvars = {}
		config = Config()

		if req.is_ajax():
			return self.ajaxhandler(req, path)

		if len(path) < 1:
			return ErrorResponse('Invalid path', request=req)

		if len(path) > 0:
			localvars['selected_type'] = 'repositories'
		if len(path) > 1:
			localvars['selected_object'] = path[1]

		try:
			if path[0] == 'show':
				return self.show(req, path[1:], localvars)
			if path[0] == 'add':
				return self.add(req, path[1:], localvars)
		except Unauthorized:
			return Redirect(config.base_url)

		return ErrorResponse('Unknown path', request=req)

	@admin_required
	def show(self, req, path, localvars):
		import os.path
		try:
			repository = Repository(path[0])
		except (IndexError, Repository.DoesNotExist):
			return ErrorResponse('This repository does not exist.', request=req)

		config = Config()
		try:
			svn_base_url = config.get('www', 'svn_base_url')
			svn_http_url = os.path.join(svn_base_url, repository.name)
		except NoOptionError:
			svn_http_url = ''

		try:
			trac_base_url = config.get('www', 'trac_base_url')
			trac_http_url = os.path.join(trac_base_url, repository.name)
		except NoOptionError:
			trac_http_url = ''

		localvars['svn_http_url'] = svn_http_url
		localvars['trac_http_url'] = trac_http_url
		localvars['repository'] = repository
		formatted = evaluate_main('repositories.html', localvars, request=req)
		return Response(formatted)

	@admin_required
	def add(self, req, path, localvars):
		config = Config()
		base_url = config.base_url

		if req.post and req.post['repository']:
			import re

			repository = req.post['repository'].value.strip()
			if re.findall('[^a-zA-Z0-9_-]', repository):
				return ErrorResponse('Invalid characters in repository name', request=req)

			url = base_url + '/repositories/show/' + repository

			reposdir = config.get('svn', 'repositories')
			newrepos = reposdir + '/' + repository
			if os.system('svnadmin create %s' % newrepos) == 0:
				repos = Repository(repository)
				repos.installPostCommitHook()
				return Redirect(url)

			return ErrorResponse('could not create repository', request=req)

		formatted = evaluate_main('newrepository.html', localvars, request=req)
		return Response(formatted)

	@admin_required
	def getsubdirs(self, req, repository):
		svn_path = req.post['getSubdirs'].value.strip('/')
		dirs = repository.getsubdirs(svn_path)
		templatevars = {'dirs': dirs}
		return XMLTemplateResponse('ajax/repositorytree.xml', templatevars)

	@admin_required
	def getpermissions(self, req, repository):
		config = Config()
		svn_path = Path(req.post['getPermissions'].value)

		perms = []
		authz_paths = [x[1] for x in repository.authz_paths]
		if str(svn_path) in authz_paths:
			perms = config.authz.permissions(repository.name, svn_path)

		users = []
		if 'userlist' in req.post:
			users = config.htpasswd.users()

		groups = []
		if 'grouplist' in req.post:
			groups = config.authz.groups()

		templatevars = {'perms': perms, 'repository': repository.name,
			'path': svn_path, 'users': users, 'groups': groups}
		return XMLTemplateResponse('ajax/repositoryperms.xml', templatevars)

	@admin_required
	def getpermissionpaths(self, req, repository):
		authz_paths = [x[1] for x in repository.authz_paths]
		templatevars = {'repository': repository.name, 'paths': authz_paths}
		return XMLTemplateResponse('ajax/repositorypermpaths.xml', templatevars)

	@admin_required
	def addpermission(self, req, repository):
		config = Config()
		name = req.post['name'].value
		type = req.post['type'].value
		path = req.post['path'].value

		# add member with no permissions (let the user select that)
		config.authz.setPermission(repository.name, path, name, type)
		config.authz.save()
		return XMLStatusResponse('addPermission', True, ('User', 'Group')[type == 'group'] + ' %s added to path %s' % (name, path))

	@admin_required
	def removepermission(self, req, repository):
		config = Config()
		name = req.post['name'].value
		type = req.post['type'].value
		path = req.post['path'].value

		config.authz.removePermission(repository.name, path, name, type)
		config.authz.save()
		return XMLStatusResponse('removePermission', True, ('User', 'Group')[type == 'group'] + ' %s removed from path %s' % (name, path))

	@admin_required
	def setpermission(self, req, repository):
		config = Config()
		name = req.post['name'].value
		type = req.post['type'].value
		path = req.post['path'].value
		permission = req.post['permission'].value

		config.authz.setPermission(repository.name, path, name, type, permission)
		config.authz.save()
		return XMLStatusResponse('setPermission', True, 'Permission for %s %s changed to %s' %
			(('user', 'group')[type == 'group'], name, permission))

	@admin_required
	def setNotifications(self, req, repository):
		enable = req.post['setNotifications'].value
		change_msg = 'enabled'
		if not enable.lower() == "true":
			change_msg = 'disabled'
			
		repository.changeNotifications(enable)
		message = 'Notifications %s' % change_msg
		templatevars = {'command': 'setNotifications',
				'enabled': str(enable), 'message': message}
		return XMLTemplateResponse('ajax/repositorynotifications.xml', 
				templatevars)

	@admin_required
	def getNotifications(self, req, repository):
		enabled = repository.notificationsEnabled()
		change_msg = 'enabled'
		if not enabled:
			change_msg = 'disabled'
		message = 'Notifications %s' % change_msg
		templatevars = {'command': 'getNotifications',
				'enabled': str(enabled), 'message': message}
		return XMLTemplateResponse('ajax/repositorynotifications.xml', 
				templatevars)

	def ajaxhandler(self, req, path):
		repositoryname = ''

		if len(path) < 2:
			return XMLStatusResponse('', False, 'Invalid path')

		action = path[0]
		repositoryname = path[1]

		try:
			repository = Repository(repositoryname)
		except (IndexError, Repository.DoesNotExist):
			return XMLStatusResponse('', False,
				'Repository %s does not exist.' % repositoryname)

		if 'getSubdirs' in req.post:
			return self.getsubdirs(req, repository)

		if 'getPermissions' in req.post:
			return self.getpermissions(req, repository)

		if 'getPermissionPaths' in req.post:
			return self.getpermissionpaths(req, repository)

		if 'addPermission' in req.post:
			return self.addpermission(req, repository)

		if 'removePermission' in req.post:
			return self.removepermission(req, repository)

		if 'setPermission' in req.post:
			return self.setpermission(req, repository)

		if 'setNotifications' in req.post:
			return self.setNotifications(req, repository)

		if 'getNotifications' in req.post:
			return self.getNotifications(req, repository)
		

		return XMLStatusResponse('', False, 'Unknown command')

