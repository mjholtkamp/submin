from config.config import Config
from __init__ import evaluate
from models.user import *
from config.authz.authz import UnknownUserError
from models.group import *
from models.repository import *

def evaluate_main(templatename, templatevariables={}, request=None):
	templatevariables['main_include'] = templatename

	config = Config()

	is_admin = False
	session_user = None
	if request and 'user' in request.session:
		try:
			session_user = request.session['user']
			is_admin = session_user.is_admin
		except UnknownUserError:
			pass

	users = listUsers(is_admin)
	groups = listGroups(is_admin)
	repositories = listRepositories(is_admin)

	xml_lists = evaluate("ajax/listall.xml", 
		{'users': users, 'groups': groups, 'repositories': repositories})
	templatevariables['main_all'] = xml_lists.replace("\n", "")
	templatevariables['main_base_url'] = config.base_url

	if request:
		templatevariables['request'] = request
		if 'user' in request.session:
			templatevariables['main_user'] = request.session['user']

	templatevariables['is_admin'] = is_admin

	return evaluate('main.html', templatevariables)
