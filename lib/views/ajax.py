from dispatch.view import View
from dispatch.response import *
from config.config import Config
from auth.decorators import *
from models.user import listUsers
from models.group import listGroups
from models.repository import listRepositories
from template import evaluate
from auth.decorators import *

class Ajax(View):
	"""Ajax view, for global ajax requests, like list users/groups/repositories"""
	@login_required
	def handler(self, req, path):
		config = Config()
		# we only handle ajax requests
		if not req.is_ajax():
			return Redirect(config.base_url)

		if 'listAll' in req.post:
			return self.listAll(req)
		if 'listUsers' in req.post:
			return self.listUsers(req)
		if 'listGroups' in req.post:
			return self.listGroups(req)
		if 'listRepositories' in req.post:
			return self.listRepositories(req)

		return XMLStatusResponse('', False, 'Unknown command')

	@admin_required
	def listAll(self, req):
		session_user = req.session['user']
		try:
			users = listUsers(session_user)
			groups = listGroups(session_user)
			repositories = listRepositories(session_user)
			return XMLTemplateResponse("ajax/listall.xml", 
				{'users': users, 'groups': groups, 'repositories': repositories})
		except Exception, e:
			return XMLStatusResponse('listAll', False, 'Failed to get a list: %s' % e)

	def listUsers(self, req):
		session_user = req.session['user']
		try:
			users = listUsers(session_user)
			return XMLTemplateResponse("ajax/listusers.xml", {'users': users})
		except Exception, e:
			return XMLStatusResponse('listUsers', False, 'Failed to get a list: %s' % e)

	def listGroups(self, req):
		try:
			groups = listGroups(req.session['user'])
			return XMLTemplateResponse("ajax/listgroups.xml", {'groups': groups})
		except Exception, e:
			return XMLStatusResponse('listGroups', False, 'Failed to get a list: %s' % e)

	def listRepositories(self, req):
		try:
			repos = listRepositories(req.session['user'])
			invalid = listRepositories(req.session['user'], only_invalid=True)
			variables = {'repositories': repos, 'invalid_repositories': invalid}
			return XMLTemplateResponse("ajax/listrepositories.xml", variables)
		except Exception, e:
			return XMLStatusResponse('listRepositories', False, 'Failed to get a list: %s' % e)

