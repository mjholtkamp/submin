# -*- coding: utf-8 -*-
from template.shortcuts import evaluate_main
from dispatch.response import Response, XMLStatusResponse, XMLTemplateResponse, Redirect
from views.error import ErrorResponse
from dispatch.view import View
from models.user import User
from models.group import Group
from models.repository import Repository, DoesNotExistError, PermissionError
from models.trac import Trac, UnknownTrac, createTracEnv
from models.options import Options
from models.exceptions import UnknownKeyError
from models.permissions import Permissions
from auth.decorators import login_required, admin_required
from path.path import Path
from unicode import uc_url_decode

class Repositories(View):
	@login_required
	def handler(self, req, path):
		localvars = {}
		o = Options()

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
		import os.path
		o = Options()

		user = req.session['user']
		try:
			repository = Repository(path[0])

			# Lie if user cannot see permission
			if not user.is_admin and not Repository.userHasReadPermissions(path[0], user):
				raise DoesNotExistError
		except DoesNotExistError:
			return ErrorResponse('This repository does not exist.', request=req)

		try:
			trac_enabled = o.value('enabled_trac')
		except UnknownKeyError:
			trac_enabled = False

		if trac_enabled:
			localvars['trac_config_ok'] = True
			localvars['trac_exists'] = False
			try:
				trac = Trac(path[0])
				localvars['trac_exists'] = True
			except UnknownTrac, e:
				pass
			except MissingConfig, e:
				localvars['trac_config_ok'] = False
				localvars['trac_msg'] = \
					'There is something missing in your config: %s' % str(e)

			trac_base_url = o.url_path('base_url_trac')
			trac_http_url = str(trac_base_url + repository.name)
			localvars['trac_http_url'] = trac_http_url

		svn_base_url = o.url_path('base_url_svn')
		svn_http_url = str(svn_base_url + repository.name)

		localvars['svn_http_url'] = svn_http_url
		localvars['repository'] = repository
		formatted = evaluate_main('repositories.html', localvars, request=req)
		return Response(formatted)

	def showAddForm(self, req, reposname, errormsg=''):
		localvars = {}
		localvars['errormsg'] = errormsg
		localvars['repository'] = reposname
		formatted = evaluate_main('newrepository.html', localvars, request=req)
		return Response(formatted)

	@admin_required
	def add(self, req, path, localvars):
		o = Options()
		base_url = o.url_path('base_url_submin')
		repository = ''

		if req.post and req.post['repository']:
			import re, commands

			repository = req.post['repository'].value.strip()
			if re.findall('[^a-zA-Z0-9_-]', repository):
				return self.showAddForm(req, repository, 'Invalid characters in repository name')

			if repository == '':
				return self.showAddForm(req, repository, 'Repository name not supplied')

			try:
				a = Repository(repository)
				return self.showAddForm(req, repository, 'Repository %s already exists' % repository)
			except DoesNotExistError:
				pass

			try:
				# TODO(michiel): Hardcode 'vcs-type' to 'svn' until vcs
				# subsystem is working properly.
				Repository.add('svn', repository)
			except PermissionError:
				return ErrorResponse('could not create repository',
					request=req, details=outtext)

			url = base_url + '/repositories/show/' + repository
			return Redirect(url)

		return self.showAddForm(req, repository)

	@admin_required
	def getsubdirs(self, req, repository):
		svn_path = req.post['getSubdirs'].value.strip('/')
		svn_path_u = uc_url_decode(svn_path) #also convert from utf-8
		dirs = repository.subdirs(svn_path_u)
		templatevars = {'dirs': dirs}
		return XMLTemplateResponse('ajax/repositorytree.xml', templatevars)

	@admin_required
	def getpermissions(self, req, repository):
		session_user = req.session['user']
		path = uc_url_decode(req.post['getPermissions'].value)
		svn_path = Path(path.encode('utf-8'))

		p = Permissions()
		perms = p.list_permissions(repository.name, str(svn_path))

		users = []
		if 'userlist' in req.post:
			usernames = User.list(session_user)

		groups = []
		if 'grouplist' in req.post:
			groupnames = Group.list(session_user)

		templatevars = {'perms': perms, 'repository': repository.name,
			'path': svn_path, 'usernames': usernames, 'groupnames': groupnames}
		return XMLTemplateResponse('ajax/repositoryperms.xml', templatevars)

	@admin_required
	def getpermissionpaths(self, req, repository):
		perms = Permissions()
		paths = perms.list_paths(repository.name)
		templatevars = {'repository': repository.name, 'paths': paths}
		return XMLTemplateResponse('ajax/repositorypermpaths.xml', templatevars)

	@admin_required
	def addpermission(self, req, repository):
		perms = Permissions()
		name = req.post['name'].value
		type = req.post['type'].value
		path = req.post['path'].value
		path = uc_url_decode(path)

		# add member with no permissions (let the user select that)
		perms.add_permission(repository.name, path, name, type, '')
		return XMLStatusResponse('addPermission', True, ('User', 'Group')[type == 'group'] + ' %s added to path %s' % (name, path))

	@admin_required
	def removepermission(self, req, repository):
		perms = Permissions()
		name = req.post['name'].value
		type = req.post['type'].value
		path = req.post['path'].value
		path = uc_url_decode(path)

		perms.remove_permission(repository.name, path, name, type)
		return XMLStatusResponse('removePermission', True, ('User', 'Group')[type == 'group'] + ' %s removed from path %s' % (name, path))

	@admin_required
	def setpermission(self, req, repository):
		perms = Permissions()
		name = req.post['name'].value
		type = req.post['type'].value
		path = req.post['path'].value
		path = uc_url_decode(path)
		permission = req.post['permission'].value

		perms.change_permission(repository.name, path, name, type, permission)
		return XMLStatusResponse('setPermission', True, 'Permission for %s %s changed to %s' %
			(('user', 'group')[type == 'group'], name, permission))

	@admin_required
	def setCommitEmails(self, req, repository):
		enable = req.post['setCommitEmails'].value.lower() == "true"
		change_msg = 'enabled'
		if not enable:
			change_msg = 'disabled'
			
		repository.enableCommitEmails(enable)
		message = 'Sending of commit emails is %s' % change_msg
		templatevars = {'command': 'setCommitEmails',
				'enabled': str(enable), 'message': message}
		return XMLTemplateResponse('ajax/repositorynotifications.xml', 
				templatevars)

	@admin_required
	def commitEmailsEnabled(self, req, repository):
		enabled = repository.commitEmailsEnabled()
		change_msg = 'enabled'
		if not enabled:
			change_msg = 'disabled'
		message = 'Notifications %s' % change_msg
		templatevars = {'command': 'commitEmailsEnabled',
				'enabled': str(enabled), 'message': message}
		return XMLTemplateResponse('ajax/repositorynotifications.xml', 
				templatevars)

	@admin_required
	def removeRepository(self, req, repository):
		repository.remove()
		return XMLStatusResponse('removeRepository', True, 'Repository %s deleted' % repository.name)

	@admin_required
	def tracEnvCreate(self, req, repository):
		(s, m) = createTracEnv(repository.name)
		if s:
			m = ""
		return XMLStatusResponse('tracEnvCreate', s, 'Trac environment "%s" created. %s' % (repository.name, m))

	def ajaxhandler(self, req, path):
		repositoryname = ''

		if len(path) < 2:
			return XMLStatusResponse('', False, 'Invalid path')

		action = path[0]
		repositoryname = path[1]
		
		try:
			repository = Repository(repositoryname)
		except (IndexError, DoesNotExistError):
			return XMLStatusResponse('', False,
				'Repository %s does not exist.' % repositoryname)

		if action == 'delete':
			return self.removeRepository(req, repository)

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

		if 'setCommitEmails' in req.post:
			return self.setCommitEmails(req, repository)

		if 'commitEmailsEnabled' in req.post:
			return self.commitEmailsEnabled(req, repository)

		if 'tracEnvCreate' in req.post:
			return self.tracEnvCreate(req, repository)

		return XMLStatusResponse('', False, 'Unknown command')

