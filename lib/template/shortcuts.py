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
	if not request or 'user' not in request.session:
		raise UnknownUserError

	session_user = request.session['user']

	templatevariables['main_base_url'] = config.base_url

	templatevariables['request'] = request
	templatevariables['main_user'] = session_user
	templatevariables['is_admin'] = session_user.is_admin

	return evaluate('main.html', templatevariables)
