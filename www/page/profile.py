from lib.utils import mimport
html = mimport('lib.html')

def printprofile():
	print '''
	<form name="" action="" method="post">
		Change password into:
		<input type="password" name="password" value="" /><br />
		Again:
		<input type="password" name="password2" value="" /><br />
		Old password:
		<input type="password" name="oldpassword" value="" /><br />
		<input type="submit" value="change" />
	</form>
	'''

def handleinput(input):
	if input.post.has_key('password') and input.post.has_key('password2') and \
	input.post.has_key('oldpassword'):
		if input.post['password'] != input.post['password2']:
			print 'passwords do not match!'
		else:
			print 'you want to change your password to: ' + input.post['password']
			return
	else:
		if input.post.has_key('password') or input.post.has_key('password2') or\
		input.post.has_key('oldpassword'):
			print 'you need to fill in every field'

	printprofile()


def handler(input):
	print html.header('profile')

	handleinput(input)

	print html.footer()
