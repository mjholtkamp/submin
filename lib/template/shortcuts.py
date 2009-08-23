from __init__ import evaluate
from models.user import User
from config.authz.authz import UnknownUserError
from models.group import Group
from models.repository import *
from models.options import Options

def evaluate_main(templatename, templatevariables={}, request=None):
	templatevariables['main_include'] = templatename

	o = Options()

	is_admin = False
	session_user = None
	if not request or 'user' not in request.session:
		raise UnknownUserError

	session_user = request.session['user']

	templatevariables['main_base_url'] = str(o.url_path('base_url_submin'))

	templatevariables['request'] = request
	templatevariables['main_user'] = session_user
	templatevariables['is_admin'] = session_user.is_admin

	return evaluate('main.html', templatevariables)
