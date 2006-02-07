from lib.utils import mimport
mod_htpasswd = mimport('lib.htpasswd')

admin = True
login_required = True

def printprofile(input):
	access_file = input.config.get('svn', 'access_file')
	htpasswd = mod_htpasswd.HTPasswd(access_file)
	users = htpasswd.users()

	print '''
	<form name="" action="" method="post">
	<div class="container">
		<b>Change user</b>
		<div class="row">
			<span class="label">User:</span>
			<select class="form" name="change_user">
				<option value="">Choose a user</option>'''

	for user in users:
		print '<option value="%s">%s</option>' % (user, user)

	print '''
			</select>
		</div>
		<div class="row">
			<span class="label">New password:</span>
			<input class="form" type="password" name="password" value="" />
		</div>
		<div class="row">
			<span class="label">Again:</span>
			<input class="form" type="password" name="password2" value="" />
		</div>
		<div class="row">
			<span class="label">&nbsp;</span>
			<input class="form" type="submit" value="Change user" />
		</div>
	</div>
	</form>
	'''

	print '''
	<form name="" action="" method="post">
	<div class="container">
		<b>Add user</b>
		<div class="row">
			<span class="label">User:</span>
			<input class="form" type="text" name="add_user" value="" />
		</div>
		<div class="row">
			<span class="label">Password:</span>
			<input class="form" type="password" name="password" value="" />
		</div>
		<div class="row">
			<span class="label">Again:</span>
			<input class="form" type="password" name="password2" value="" />
		</div>
		<div class="row">
			<span class="label">&nbsp;</span>
			<input class="form" type="submit" value="Add user" />
		</div>
	</div>
	</form>
	'''

	print '''
	<form name="" action="" method="post">
	<div class="container">
		<b>Remove user</b>
		<div class="row">
			<span class="label">User:</span>
			<select class="form" name="remove_user">
				<option value="">Choose a user</option>'''

	for user in users:
		print '<option value="%s">%s</option>' % (user, user)

	print '''
			</select>
		</div>
		<div class="row">
			<span class="label">&nbsp;</span>
			<input class="form" type="submit" value="Remove user" />
		</div>
	</div>
	</form>
	'''

def handleinput(input):
	change = input.post.has_key('change_user')
	add = input.post.has_key('add_user')
	remove = input.post.has_key('remove_user')

	if ((input.post.has_key('password') and input.post.has_key('password2')) 
	and (change or add)):
		if input.post['password'] != input.post['password2']:
			print 'passwords do not match!'
		else:
			password = input.post['password']

			if input.post.has_key('change_user'):
				changepassword(input, input.post['change_user'], passord)
			if input.post.has_key('add_user'):
				adduser(input, input.post['add_user'], password)

			return
	else:
		if input.post.has_key('password') or input.post.has_key('password2') or\
		input.post.has_key('user') or input.post.has_key('add_user'):
			print 'you need to fill in every field'

	if remove:
		removeuser(input, input.post['remove_user'])

	printprofile(input)

def changepassword(input, user, password):
	if user is None:
		print 'Nobody is logged in!'
		return

	access_file = input.config.get('svn', 'access_file')
	htpasswd = mod_htpasswd.HTPasswd(access_file)
	htpasswd.change(user, password)
	htpasswd.flush()
	print 'Password changed<br />'

def adduser(input, user, password):
	access_file = input.config.get('svn', 'access_file')
	htpasswd = mod_htpasswd.HTPasswd(access_file)
	htpasswd.add(user, password)
	htpasswd.flush()
	print 'User ' + user + ' added<br />'

def removeuser(input, user):
	access_file = input.config.get('svn', 'access_file')
	htpasswd = mod_htpasswd.HTPasswd(access_file)
	htpasswd.remove(user)
	htpasswd.flush()
	print 'User ' + user + ' removed<br />'

def handler(input):
	print input.html.header('users')

	handleinput(input)

	print input.html.footer()
