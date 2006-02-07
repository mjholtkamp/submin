from lib.utils import mimport
from mod_python import Session

login_required = False

def handler(input):
	olduser = None

	if input.isLoggedIn():
		olduser = input.session['user']
		input.deleteSession()

	print input.html.header('Main screen turn on')

	if olduser:
		print 'Hello %s, you are now logged out' % olduser
	else:
		print 'Nobody is logged in'

	print input.html.footer()
