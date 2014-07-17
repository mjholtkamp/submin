from submin.models.exceptions import UnknownUserError
from submin.models import options
from submin.models.user import User
from submin.template.template import Template
from . import template_commands
from submin import VERSION

def evaluate(templatename, localvars={}):
	import os
	template_path = options.static_path('templates')
	templatename = str(template_path + templatename)
	localvars['SUBMIN_VERSION'] = VERSION
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

	is_admin = False
	session_user = None
	if not request or 'user' not in request.session:
		raise UnknownUserError

	session_user = User(request.session['user']['name'])

	templatevariables['main_base_url'] = str(options.url_path('base_url_submin'))
	templatevariables['session_user'] = session_user

	return evaluate('main.html', templatevariables)
