from lib.utils import mimport
mod_htpasswd = mimport('lib.htpasswd')

admin = True
login_required = True

def printprofile(input):
	access_file = input.config.get('svn', 'access_file')
	htpasswd = mod_htpasswd.HTPasswd(access_file)
	users = htpasswd.users()

	print '''
	<form name="" action="%s/users" method="post">
	<div class="container">
		<b>Change user</b>
		<div class="row">
			<label for="change_user">User:</label>
			<select class="form" name="change_user" id="change_user">
				<option value="">Choose a user</option>''' % input.base

	for user in users:
		print '<option value="%s">%s</option>' % (user, user)

	print '''
			</select>
		</div>
		<div class="row">
			<label for="password">New password:</label>
			<input class="form" type="password" name="password" value="" id="password" />
		</div>
		<div class="row">
			<label for="password2">Again:</label>
			<input class="form" type="password" name="password2" value="" id="password2" />
		</div>
		<div class="row">
			<label>&nbsp;</label>
			<input class="form" type="submit" value="Change user" />
		</div>
	</div>
	</form>
	'''

	print '''
	<form name="" action="%s/users" method="post">
	<div class="container">
		<b>Add user</b>
		<div class="row">
			<label for="add_user">User:</label>
			<input class="form" type="text" name="add_user" value="" id="add_user" />
		</div>
		<div class="row">
			<label for="add_password">Password:</label>
			<input class="form" type="password" name="password" value="" id="add_password" />
		</div>
		<div class="row">
			<label for="add_password2">Again:</label>
			<input class="form" type="password" name="password2" value="" id="add_password2" />
		</div>
		<div class="row">
			<label>&nbsp;</label>
			<input class="form" type="submit" value="Add user" />
		</div>
	</div>
	</form>
	''' % input.base

	print '''
	<form name="" action="%s/users" method="post">
	<div class="container">
		<b>Remove user</b>
		<div class="row">
			<label for="remove_user">User:</label>
			<select class="form" name="remove_user" id="remove_user">
				<option value="">Choose a user</option>''' % input.base

	for user in users:
		print '<option value="%s">%s</option>' % (user, user)

	print '''
			</select>
		</div>
		<div class="row">
			<label>&nbsp;</label
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
				changepassword(input, input.post['change_user'], password)
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
