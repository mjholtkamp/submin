import os
import sys

from unicode import uc_str
from template import Template
from config.config import Config
import template_commands

def evaluate(templatename, localvars={}):
	config = Config()
	templatename = str(config.template_path + templatename)
	oldcwd = os.getcwd()
	if os.path.dirname(templatename):
		os.chdir(os.path.dirname(templatename))

	fp = open(os.path.basename(templatename), 'r')
	evaluated_string = ''
	if fp:
		lines = uc_str(''.join(fp.readlines()), 'utf-8')
		template = Template(lines, localvars)
		evaluated_string = template.evaluate()

		fp.close()

	if os.path.dirname(templatename):
		os.chdir(oldcwd)

	return evaluated_string

if __name__ == "__main__":
	from tests import *
	runtests()
