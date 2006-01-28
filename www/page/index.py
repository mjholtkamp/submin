from lib.utils import mimport
html = mimport('lib.html')

def handler(input):
	print html.header('Main screen turn on')

	print '''
		<ul>
			<li />change your <a href="profile">profile</a>
			<li />set permissions <a href="authz">permissions</a>
		</ul>
		'''

	print html.footer()
