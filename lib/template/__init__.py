import os
import sys

from template import Template
import template_commands

def evaluate(templatename, localvars={}):
    oldcwd = os.getcwd()
    if os.path.dirname(templatename):
	    os.chdir(os.path.dirname(templatename))
    
    fp = open(os.path.basename(templatename), 'r')
    evaluated_string = ''
    if fp:
	    lines = ''.join(fp.readlines())
	    template = Template(lines, localvars)
	    evaluated_string = template.evaluate()
	    
	    fp.close()

    if os.path.dirname(templatename):
	    os.chdir(oldcwd)

    return evaluated_string

if __name__ == "__main__":
	from tests import *
	runtests()
