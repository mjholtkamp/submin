from lib.utils import mimport
html = mimport('lib.html')

def handler(input):
	print html.header('Permissions')
	print '<h2>Permissions</h2>'
	print html.footer()
