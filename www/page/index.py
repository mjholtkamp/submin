from lib.utils import mimport

def handler(input):
	print input.html.header('Main screen turn on')

	print '''This is the main site. Please select 'profile' in the
	menu on the left to change your password or 'permissions' to
	set permissions on users, groups and projects.'''

	print input.html.footer()
