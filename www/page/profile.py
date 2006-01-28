from lib.utils import mimport
html = mimport('lib.html')
mod_htpasswd = mimport('lib.htpasswd')

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
			changepassword(input)
			return
	else:
		if input.post.has_key('password') or input.post.has_key('password2') or\
		input.post.has_key('oldpassword'):
			print 'you need to fill in every field'

	printprofile()

def changepassword(input):
	pw = input.req.get_basic_auth_pw()
	user = input.req.user
	password = input.post['password']
	oldpassword = input.post['oldpassword']
	htpasswd = mod_htpasswd.HTPasswd('/usr/local/submerge/.htpasswd')
	if htpasswd.check(user, oldpassword):
		htpasswd.change(user, password)
		htpasswd.flush()
		print 'Password changed<br />'
	else:
		print 'Old password incorrect!<br />'


def handler(input):
	print html.header('profile')

	print '<a href=".">main page</a><br />'
	handleinput(input)

	print html.footer()
