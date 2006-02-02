from lib.utils import mimport
mod_htpasswd = mimport('lib.htpasswd')

def printprofile():
	print '''
	<form name="" action="" method="post">
	<div class="container">
		<div class="row">
			<span class="label">Change password into:</span>
			<input class="form" type="password" name="password" value="" />
		</div>
		<div class="row">
			<span class="label">Again:</span>
			<input class="form" type="password" name="password2" value="" />
		</div>
		<div class="row">
			<span class="label">Old password:</span>
			<input class="form" type="password" name="oldpassword" value="" />
		</div>
		<div class="row">
			<span class="label">&nbsp;</span>
			<input class="form" type="submit" value="change" />
		</div>
	</div>
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
	if user is None:
		print 'Nobody is logged in!'
		return
	
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
	print input.html.header('profile')

	handleinput(input)

	print input.html.footer()
