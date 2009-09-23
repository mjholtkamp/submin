from models.user import User
from config.authz.authz import UnknownUserError
from models.group import Group
from models.repository import *
from models.options import Options
from unicode import uc_str
from template import Template
import template_commands
from path.path import Path

def evaluate(templatename, localvars={}):
	o = Options()
	template_path = o.static_path('templates')
	templatename = str(template_path + templatename)
	oldcwd = os.getcwd()
	if os.path.dirname(templatename):
		os.chdir(os.path.dirname(templatename))

	fp = open(os.path.basename(templatename), 'r')
	evaluated_string = ''
	if fp:
		template = Template(fp, localvars)
		evaluated_string = template.evaluate()

		fp.close()

	if os.path.dirname(templatename):
		os.chdir(oldcwd)

	return evaluated_string


def evaluate_main(templatename, templatevariables={}, request=None):
	templatevariables['main_include'] = templatename

	o = Options()

	is_admin = False
	session_user = None
	if not request or 'user' not in request.session:
		raise UnknownUserError

	session_user = request.session['user']

	templatevariables['main_base_url'] = str(o.url_path('base_url_submin'))
	templatevariables['session_user'] = session_user

	return evaluate('main.html', templatevariables)
