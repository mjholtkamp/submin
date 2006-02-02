from lib.utils import mimport
html = mimport('lib.html')

def handler(input):
	print html.header('Main screen turn on')

	print '''This is the main site. Please select 'profile' in the
	menu on the left to change your password or 'permissions' to
	set permissions on users, groups and projects.'''

	print html.footer()
