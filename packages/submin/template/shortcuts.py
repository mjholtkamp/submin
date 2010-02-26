from submin.models.exceptions import UnknownUserError
from submin.models import options
from submin.template.template import Template
import template_commands

def evaluate(templatename, localvars={}):
	import os
	template_path = options.static_path('templates')
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

	is_admin = False
	session_user = None
	if not request or 'user' not in request.session:
		raise UnknownUserError

	session_user = request.session['user']

	templatevariables['main_base_url'] = str(options.url_path('base_url_submin'))
	templatevariables['session_user'] = session_user

	return evaluate('main.html', templatevariables)
