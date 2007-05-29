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

def test():
	template=r"""[set:test2 5][include test_templates/test][set:test 3]here be dragons
[val included_val]
[test:included_val In de main-file gaat test:included_val goed!]
[else In de main-file gaat test:included_val niet goed!]
[val test][set:bla true][set:waarheid true]
[val test2][set:bla test][set:test 42]
This will give no error or warning: [val test3]
[iter:users some html [ival] code here<br />] 
[test:waarheid Test-test: The variable bla is set to '[val bla]'<br />]
[else Else-test is executed incorrectly]
[test:onwaar foo]
[else Else-test is executed correctly]

[iter:object_list new User('[ival.name]', '[ival.email]');
]

Item 0 uit users: [val users.0]
Item foo uit dict: [val dict.foo]
Item dict.baz uit dict: [val dict.dict.baz]

[iter:list_list loop: [iter:ival inner ival: [ival] ]
]

[test:users.0 users.0 is evaluated as True!] [else the test for users.0 did go wrong!]

[test:users.9 users.9 is evaluated as True, which is incorrect!][else the test users.9 evaluated as False, which is correct!]
\[escaping also works!\] \foo
"""

	localvars = {}
	class User:
		def __init__(self, name, email):
			self.name = name
			self.email = email
		
		def function(self):
			return 'function!'
			
	users = ['sabre2th', 'avaeq', 'will', 'tux']
	object_list = [User('sabre2th', 'x@elfstone.nl')]
	object_list.append(User('avaeq', 'x@webdevel.nl'))
	localvars['users'] = users
	localvars['object_list'] = object_list
	localvars['dict'] = {'foo': 'bar', 'dict': {'baz': 'quux'}}
	
	list_list = [['foo', 'bar'], ['baz', 'quux']]
	localvars['list_list'] = list_list
	tpl = Template(template, localvars)
	if len(sys.argv) > 1:
		print tpl.parse_tree()
		print '='*78
	print tpl.evaluate()

if __name__ == "__main__":
	test()
