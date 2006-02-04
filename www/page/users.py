from lib.utils import mimport
mod_htpasswd = mimport('lib.htpasswd')

def printprofile():
	htpasswd = mod_htpasswd.HTPasswd('/usr/local/submerge/.htpasswd')
	users = htpasswd.users()

	print '''
	<form name="" action="" method="post">
	<div class="container">
		<div class="row">
			<span class="label">User:</span>
			<select class="form" name="user">
				<option value="">Choose a user</option>'''

	for user in users:
		print '<option value="%s">%s</option>' % (user, user)

	print '''
			</select>
		</div>
		<div class="row">
			<span class="label">Change password into:</span>
			<input class="form" type="password" name="password" value="" />
		</div>
		<div class="row">
			<span class="label">Again:</span>
			<input class="form" type="password" name="password2" value="" />
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
	input.post.has_key('user'):
		if input.post['password'] != input.post['password2']:
			print 'passwords do not match!'
		else:
			changepassword(input, input.post['user'])
			return
	else:
		if input.post.has_key('password') or input.post.has_key('password2') or\
		input.post.has_key('user'):
			print 'you need to fill in every field'

	printprofile()

def changepassword(input, user):
	pw = input.req.get_basic_auth_pw()
	if user is None:
		print 'Nobody is logged in!'
		return
	
	password = input.post['password']
	htpasswd = mod_htpasswd.HTPasswd('/usr/local/submerge/.htpasswd')
	htpasswd.change(user, password)
	htpasswd.flush()
	print 'Password changed<br />'

def handler(input):
	print input.html.header('users')

	handleinput(input)

	print input.html.footer()
