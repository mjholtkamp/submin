# -*- coding: utf-8 -*-
from submin.template.shortcuts import evaluate_main
from submin.dispatch.response import Response, XMLStatusResponse, XMLTemplateResponse, Redirect
from submin.views.error import ErrorResponse
from submin.dispatch.view import View
from submin.models import user
from submin.models import group
from submin.models.repository import Repository, DoesNotExistError, PermissionError
from submin.models.trac import Trac, UnknownTrac, createTracEnv
from submin.models import options
from submin.models.exceptions import UnknownKeyError
from submin.models.permissions import Permissions
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
			repository = Repository(path[0], vcs_type)

			# Lie if user has no permission to read
			if not u.is_admin and not Repository.userHasReadPermissions(path[0], u):
				raise DoesNotExistError
		except DoesNotExistError:
			return ErrorResponse('This repository does not exist.', request=req)

		try:
			trac_enabled = options.value('enabled_trac')
		except UnknownKeyError:
			trac_enabled = False

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

			# this chops off the .git for git repositories, not for svn
			repos_name = repository.name.replace(".git", "")

			trac_base_url = options.url_path('base_url_trac')
			trac_http_url = str(trac_base_url + repos_name)
			templatevars['trac_http_url'] = trac_http_url

		vcs_url_error_msgs = {
				"git": "Please make sure both git_user and git_ssh_host settings are set",
				"svn": "base_url_svn not set in config",
		}

		try:
			vcs_url = self.get_url(repository)
		except UnknownKeyError:
			vcs_url = ""
			templatevars['vcs_url_error'] = vcs_url_error_msgs[repository.vcs_type]

		templatevars['vcs_url'] = vcs_url
		templatevars['repository'] = repository
		templatevars['vcs_type'] = vcs_type
		formatted = evaluate_main('repositories.html', templatevars, request=req)
		return Response(formatted)

	def get_url(self, repository):
		if repository.vcs_type == 'git':
			git_user = options.value("git_user")
			git_host = options.value("git_ssh_host")
			git_port = options.value("git_ssh_port")
			return  'ssh://%s@%s:%s/%s' % (git_user, git_host, git_port, repository.name)

		vcs_base_url = options.url_path('base_url_%s' % repository.vcs_type)
		return str(vcs_base_url + repository.name)

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
		repository = ''

		if req.post and req.post['repository']:
			import re, commands

			repository = req.post.get('repository').strip()
			if re.findall('[^a-zA-Z0-9_-]', repository):
				return self.showAddForm(req, repository, 'Invalid characters in repository name')

			if "vcs" not in req.post or req.post.get("vcs").strip() == "":
				return self.showAddForm(req, repository, "No repository type selected. Please select a repository type.")

			vcs_type = req.post.get("vcs").strip()

			if repository == '':
				return self.showAddForm(req, repository, 'Repository name not supplied')

			if vcs_type not in vcs_list():
				return self.showAddForm(req, repository, "Invalid repository type supplied.")

			try:
				a = Repository(repository, vcs_type)
				return self.showAddForm(req, repository, 'Repository %s already exists' % repository)
			except DoesNotExistError:
				pass

			try:
				asking_user = user.User(req.session['user'])
				Repository.add(vcs_type, repository, asking_user)
			except PermissionError, e:
				return ErrorResponse('could not create repository',
					request=req, details=str(e))

			url = '%s/repositories/show/%s/%s' % (base_url, vcs_type,
					repository)
			return Redirect(url, req)

		return self.showAddForm(req, repository)

	@admin_required
	def getsubdirs(self, req, repository):
		svn_path = req.post.get('getSubdirs').strip('/')
		dirs = repository.subdirs(svn_path)
		templatevars = {'dirs': dirs}
		return XMLTemplateResponse('ajax/repositorytree.xml', templatevars)

	@admin_required
	def getpermissions(self, req, repository):
		session_user = req.session['user']
		asking_user = user.User(session_user['name'])
		path = req.post.get('getPermissions')
		branch_or_path = Path(path)

		p = Permissions()
		perms = p.list_permissions(repository.name, repository.vcs_type,
				path)

		usernames = []
		if 'userlist' in req.post:
			usernames = user.list(asking_user)

		groupnames = []
		if 'grouplist' in req.post:
			groupnames = group.list(asking_user)

		templatevars = {'perms': perms, 'repository': repository.name,
			'path': branch_or_path, 'usernames': usernames,
			'groupnames': groupnames}
		return XMLTemplateResponse('ajax/repositoryperms.xml', templatevars)

	@admin_required
	def getpermissionpaths(self, req, repository):
		perms = Permissions()
		paths = perms.list_paths(repository.name, repository.vcs_type)
		templatevars = {'repository': repository.name, 'paths': paths}
		return XMLTemplateResponse('ajax/repositorypermpaths.xml', templatevars)

	@admin_required
	def addpermission(self, req, repository):
		perms = Permissions()
		name = req.post.get('name')
		type = req.post.get('type')
		path = req.post.get('path')
		vcs_type = repository.vcs_type

		default_perm = ''
		if vcs_type == "git":
			if path != "/":
				default_perm = "w"
			else:
				default_perm = "r"

		perms.add_permission(repository.name, repository.vcs_type, path, name,
				type, default_perm)
		return XMLStatusResponse('addPermission', True, ('User', 'Group')[type == 'group'] + ' %s added to path %s' % (name, path))

	@admin_required
	def removepermission(self, req, repository):
		perms = Permissions()
		name = req.post.get('name')
		type = req.post.get('type')
		path = req.post.get('path')

		perms.remove_permission(repository.name, repository.vcs_type, path,
				name, type)
		return XMLStatusResponse('removePermission', True, ('User', 'Group')[type == 'group'] + ' %s removed from path %s' % (name, path))

	@admin_required
	def setpermission(self, req, repository):
		perms = Permissions()
		name = req.post.get('name')
		type = req.post.get('type')
		path = req.post.get('path')
		permission = req.post.get('permission')

		perms.change_permission(repository.name, repository.vcs_type, path,
				name, type, permission)
		return XMLStatusResponse('setPermission', True, 'Permission for %s %s changed to %s' %
			(('user', 'group')[type == 'group'], name, permission))

	@admin_required
	def setCommitEmails(self, req, repository):
		enable = req.post.get('setCommitEmails').lower() == "true"
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
		repos_name = repository.name.replace(".git", "")
		asking_user = user.User(req.session['user']['name'])
		createTracEnv(repos_name, asking_user)
		return XMLStatusResponse('tracEnvCreate', True, 'Trac environment "%s" created.' % repos_name)

	def ajaxhandler(self, req, path):
		repositoryname = ''

		if len(path) < 3:
			return XMLStatusResponse('', False, 'Invalid path')

		action = path[0]
		vcs_type = path[1]
		repositoryname = path[2]

		repository = None
		try:
			repository = Repository(repositoryname, vcs_type)
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

