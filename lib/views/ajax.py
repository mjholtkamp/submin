from dispatch.view import View
from dispatch.response import *
from config.config import Config
from auth.decorators import *
from models.user import listUsers
from models.group import listGroups
from models.repository import listRepositories
from template import evaluate

class Ajax(View):
	"""Ajax view, for global ajax requests, like list users/groups/repositories"""
	def handler(self, req, path):
		config = Config()
		# we only handle ajax requests
		if not req.is_ajax():
			return Redirect(config.base_url)

		if 'listAll' in req.post:
			return self.listAll(req)
		
		return XMLStatusResponse('', False, 'Unknown command')
		
	def listAll(self, req):
		is_admin = req.session['user'].is_admin
		try:
			users = listUsers(is_admin)
			groups = listGroups(is_admin)
			repositories = listRepositories(is_admin)
			return XMLTemplateResponse("ajax/listall.xml", 
				{'users': users, 'groups': groups, 'repositories': repositories})
		except Exception, e:
			return XMLStatusResponse('listAll', False, 'Failed to get a list: %s' % e)
