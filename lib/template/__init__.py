import os
import sys

from unicode import uc_str
from template import Template
import template_commands
from models.options import Options
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
