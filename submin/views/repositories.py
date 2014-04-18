# -*- coding: utf-8 -*-
from submin.template.shortcuts import evaluate_main
from submin.dispatch.response import Response, XMLStatusResponse, XMLTemplateResponse, Redirect
from submin.views.error import ErrorResponse
from submin.dispatch.view import View
from submin.models import user
from submin.models import group
from submin.models import permissions
from submin.models import repository
from submin.models.repository import Repository, DoesNotExistError, PermissionError
from submin.models.trac import Trac, UnknownTrac, createTracEnv
from submin.models import options
from submin.models.exceptions import UnknownKeyError
from submin.models.repository import vcs_list
from submin.auth.decorators import login_required, admin_required
from submin.path.path import Path

class Repositories(View):
	@login_required
	def handler(self, req, path):
		templatevars = {}

		if req.is_ajax():
			return self.ajaxhandler(req, path)

		if len(path) < 1 or (path[0] == "show" and len(path) < 3):
			return ErrorResponse('Invalid path', request=req)

		if len(path) > 0:
			templatevars['selected_type'] = 'repositories'
		if len(path) > 2:
			templatevars['selected_object'] = path[2]

		if path[0] == 'show':
			return self.show(req, path[1], path[2:], templatevars)
		if path[0] == 'add':
			return self.add(req, path[1:], templatevars)

		return ErrorResponse('Unknown path', request=req)

	def show(self, req, vcs_type, path, templatevars):
		import os.path

		u = user.User(req.session['user']['name'])
		try:
			repos = Repository(path[0], vcs_type)

			# Lie if user has no permission to read
			if not u.is_admin and not repository.userHasReadPermissions(u.name, path[0], vcs_type):
				raise DoesNotExistError
		except DoesNotExistError:
			return ErrorResponse('This repository does not exist.', request=req)

		trac_enabled = options.value('enabled_trac', 'no') != 'no'

		if trac_enabled:
			templatevars['trac_config_ok'] = True
			templatevars['trac_exists'] = False
			try:
				trac = Trac(path[0])
				templatevars['trac_exists'] = True
			except UnknownTrac, e:
				pass
			except MissingConfig, e:
				templatevars['trac_config_ok'] = False
				templatevars['trac_msg'] = \
					'There is something missing in your config: %s' % str(e)

			trac_base_url = options.url_path('base_url_trac')
			trac_http_url = str(trac_base_url + repos.name)
			templatevars['trac_http_url'] = trac_http_url

		vcs_url_error_msgs = {
				"git": "Please make sure both git_user and git_ssh_host settings are set",
				"svn": "base_url_svn not set in config",
				"mock": "Please make sure both mock_dir and base_url_mock are set",
		}

		try:
			vcs_url = repos.url()
		except UnknownKeyError:
			vcs_url = ""
			templatevars['vcs_url_error'] = vcs_url_error_msgs[repos.vcs_type]

		templatevars['vcs_url'] = vcs_url
		templatevars['repository'] = repos
		templatevars['vcs_type'] = vcs_type
		formatted = evaluate_main('repositories.html', templatevars, request=req)
		return Response(formatted)

	def showAddForm(self, req, reposname, errormsg=''):
		templatevars = {}
		templatevars['errormsg'] = errormsg
		templatevars['repository'] = reposname
		templatevars["systems"] = vcs_list()
		formatted = evaluate_main('newrepository.html', templatevars, request=req)
		return Response(formatted)

	@admin_required
	def add(self, req, path, templatevars):
		base_url = options.url_path('base_url_submin')
		reposname = ''

		if req.post and req.post['repository']:
			import re, commands

			reposname = req.post.get('repository').strip()
			if re.findall('[^a-zA-Z0-9_-]', reposname):
				return self.showAddForm(req, reposname, 'Invalid characters in repository name')

			if "vcs" not in req.post or req.post.get("vcs").strip() == "":
				return self.showAddForm(req, reposname, "No repository type selected. Please select a repository type.")

			vcs_type = req.post.get("vcs").strip()

			if reposname == '':
				return self.showAddForm(req, reposname, 'Repository name not supplied')

			if vcs_type not in vcs_list():
				return self.showAddForm(req, reposname, "Invalid repository type supplied.")

			try:
				a = Repository(reposname, vcs_type)
				return self.showAddForm(req, reposname, 'Repository %s already exists' % reposname)
			except DoesNotExistError:
				pass

			try:
				asking_user = user.User(req.session['user']['name'])
				Repository.add(vcs_type, reposname, asking_user)
			except PermissionError, e:
				return ErrorResponse('could not create repository',
					request=req, details=str(e))

			url = '%s/repositories/show/%s/%s' % (base_url, vcs_type,
					reposname)
			return Redirect(url, req)

		return self.showAddForm(req, reposname)

	@admin_required
	def getsubdirs(self, req, repos):
		svn_path = req.post.get('getSubdirs').strip('/')
		dirs = repos.subdirs(svn_path)
		templatevars = {'dirs': dirs}
		return XMLTemplateResponse('ajax/repositorytree.xml', templatevars)

	@admin_required
	def getpermissions(self, req, repos):
		session_user = req.session['user']
		asking_user = user.User(session_user['name'])
		path = req.post.get('getPermissions')
		branch_or_path = Path(path)

		perms = permissions.list_by_path(repos.name,
				repos.vcs_type, path)

		usernames = []
		if 'userlist' in req.post:
			usernames = user.list(asking_user)

		groupnames = []
		if 'grouplist' in req.post:
			groupnames = group.list(asking_user)

		templatevars = {'perms': perms, 'repository': repos.name,
			'path': branch_or_path, 'usernames': usernames,
			'groupnames': groupnames}
		return XMLTemplateResponse('ajax/repositoryperms.xml', templatevars)

	@admin_required
	def getpermissionpaths(self, req, repos):
		paths = permissions.list_paths(repos.name, repos.vcs_type)
		templatevars = {'repository': repos.name, 'paths': paths}
		return XMLTemplateResponse('ajax/repositorypermpaths.xml', templatevars)

	@admin_required
	def addpermission(self, req, repos):
		name = req.post.get('name')
		type = req.post.get('type')
		path = req.post.get('path')
		vcs_type = repos.vcs_type

		default_perm = ''
		if vcs_type == "git":
			if path != "/":
				default_perm = "w"
			else:
				default_perm = "r"

		permissions.add(repos.name, repos.vcs_type, path, name,
				type, default_perm)
		return XMLStatusResponse('addPermission', True, ('User', 'Group')[type == 'group'] + ' %s added to path %s' % (name, path))

	@admin_required
	def removepermission(self, req, repos):
		name = req.post.get('name')
		type = req.post.get('type')
		path = req.post.get('path')

		permissions.remove(repos.name, repos.vcs_type, path,
				name, type)
		return XMLStatusResponse('removePermission', True, ('User', 'Group')[type == 'group'] + ' %s removed from path %s' % (name, path))

	@admin_required
	def setpermission(self, req, repos):
		name = req.post.get('name')
		type = req.post.get('type')
		path = req.post.get('path')
		permission = req.post.get('permission')

		permissions.change(repos.name, repos.vcs_type, path,
				name, type, permission)
		return XMLStatusResponse('setPermission', True, 'Permission for %s %s changed to %s' %
			(('user', 'group')[type == 'group'], name, permission))

	@admin_required
	def setCommitEmails(self, req, repos):
		enable = req.post.get('setCommitEmails').lower() == "true"
		change_msg = 'enabled'
		if not enable:
			change_msg = 'disabled'
			
		repos.enableCommitEmails(enable)
		message = 'Sending of commit emails is %s' % change_msg
		templatevars = {'command': 'setCommitEmails',
				'enabled': str(enable), 'message': message}
		return XMLTemplateResponse('ajax/repositorynotifications.xml', 
				templatevars)

	@admin_required
	def commitEmailsEnabled(self, req, repos):
		enabled = repos.commitEmailsEnabled()
		change_msg = 'enabled'
		if not enabled:
			change_msg = 'disabled'
		message = 'Notifications %s' % change_msg
		templatevars = {'command': 'commitEmailsEnabled',
				'enabled': str(enabled), 'message': message}
		return XMLTemplateResponse('ajax/repositorynotifications.xml', 
				templatevars)

	@admin_required
	def setTracCommitHook(self, req, repos):
		enable = req.post.get('setTracCommitHook').lower() == "true"
		change_msg = 'enabled'
		if not enable:
			change_msg = 'disabled'
			
		repos.enableTracCommitHook(enable)
		message = 'Trac commit hook is %s' % change_msg
		templatevars = {'command': 'setTracCommitHook',
				'enabled': str(enable), 'message': message}
		return XMLTemplateResponse('ajax/repositorynotifications.xml', 
				templatevars)

	@admin_required
	def commitEmailsEnabled(self, req, repos):
		enabled = repos.tracCommitHookEnabled()
		change_msg = 'enabled'
		if not enabled:
			change_msg = 'disabled'
		message = 'Notifications %s' % change_msg
		templatevars = {'command': 'tracCommitHookEnabled',
				'enabled': str(enabled), 'message': message}
		return XMLTemplateResponse('ajax/repositorynotifications.xml', 
				templatevars)


	@admin_required
	def removeRepository(self, req, repos):
		repos.remove()
		return XMLStatusResponse('removeRepository', True,
				'Repository %s deleted' % repos.name)

	@admin_required
	def tracEnvCreate(self, req, repos):
		asking_user = user.User(req.session['user']['name'])
		createTracEnv(repos.name, asking_user)
		return XMLStatusResponse('tracEnvCreate', True,
				'Trac environment "%s" created.' % repos.name)

	def ajaxhandler(self, req, path):
		reposname = ''

		if len(path) < 3:
			return XMLStatusResponse('', False, 'Invalid path')

		action = path[0]
		vcs_type = path[1]
		reposname = path[2]

		repos = None
		try:
			repos = Repository(reposname, vcs_type)
		except (IndexError, DoesNotExistError):
			return XMLStatusResponse('', False,
				'Repository %s does not exist.' % reposname)

		if action == 'delete':
			return self.removeRepository(req, repos)

		if 'getSubdirs' in req.post:
			return self.getsubdirs(req, repos)

		if 'getPermissions' in req.post:
			return self.getpermissions(req, repos)

		if 'getPermissionPaths' in req.post:
			return self.getpermissionpaths(req, repos)

		if 'addPermission' in req.post:
			return self.addpermission(req, repos)

		if 'removePermission' in req.post:
			return self.removepermission(req, repos)

		if 'setPermission' in req.post:
			return self.setpermission(req, repos)

		if 'setCommitEmails' in req.post:
			return self.setCommitEmails(req, repos)

		if 'commitEmailsEnabled' in req.post:
			return self.commitEmailsEnabled(req, repos)

		if 'setTracCommitHook' in req.post:
			return self.setTracCommitHook(req, repos)

		if 'tracCommitHookEnabled' in req.post:
			return self.tracCommitHookEnabled(req, repos)

		if 'tracEnvCreate' in req.post:
			return self.tracEnvCreate(req, repos)

		return XMLStatusResponse('', False, 'Unknown command')

