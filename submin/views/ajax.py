from submin.dispatch.view import View
from submin.dispatch.response import *
from submin.auth.decorators import *
from submin.models import user
from submin.models import group
from submin.models.repository import Repository
from submin.models import options

class Ajax(View):
	"""Ajax view, for global ajax requests, like list users/groups/repositories"""
	@login_required
	def handler(self, req, path):
		# we only handle ajax requests
		if not req.is_ajax():
			return Redirect(options.url_path('base_url_submin'), req)

		if 'listAll' in req.post:
			return self.listAll(req)
		if 'listUsers' in req.post:
			return self.listUsers(req)
		if 'listGroups' in req.post:
			return self.listGroups(req)
		if 'listRepositories' in req.post:
			return self.listRepositories(req)

		return XMLStatusResponse('', False, 'Unknown command')

	def listUsers(self, req):
		session_user = req.session['user']
		try:
			usernames = user.list(session_user)
			return XMLTemplateResponse("ajax/listusers.xml", {'usernames': usernames})
		except Exception, e:
			return XMLStatusResponse('listUsers', False, 'Failed to get a list: %s' % e)

	def listGroups(self, req):
		try:
			groupnames = group.list(req.session['user'])
			return XMLTemplateResponse("ajax/listgroups.xml", {'groupnames': groupnames})
		except Exception, e:
			raise
			return XMLStatusResponse('listGroups', False, 'Failed to get a list: %s' % e)

	def listRepositories(self, req):
		try:
			repos = Repository.list(req.session['user'])
			variables = {'repositories': repos}
			return XMLTemplateResponse("ajax/listrepositories.xml", variables)
		except Exception, e:
			raise
			return XMLStatusResponse('listRepositories', False, 'Failed to get a list: %s' % e)

