from lib.utils import mimport
mod_htpasswd = mimport('lib.htpasswd')

login_required = True

def printprofile(input):
	print '''
	<form name="" action="%s/profile" method="post">
	<div class="container">
		<div class="row">
			<label for="password">Change password into:</label>
			<input class="form" type="password" name="password" value="" id="password" />
		</div>
		<div class="row">
			<label for="password2">Again:</label>
			<input class="form" type="password" name="password2" value="" id="password2" />
		</div>
		<div class="row">
			<label for="oldpassword">Old password:</label>
			<input class="form" type="password" name="oldpassword" value="" id="oldpassword" />
		</div>
		<div class="row">
			<label>&nbsp;</label>
			<input class="form" type="submit" value="change" />
		</div>
	</div>
	</form>
	''' % input.base

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

	printprofile(input)

def changepassword(input):
	user = input.user
	if user is None:
		print 'Nobody is logged in!'
		return
	
	password = input.post['password']
	oldpassword = input.post['oldpassword']
	access_file = input.config.get('svn', 'access_file')
	htpasswd = mod_htpasswd.HTPasswd(access_file)
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
