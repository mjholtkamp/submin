from lib.utils import mimport
mod_htpasswd = mimport('lib.htpasswd')

admin = True
login_required = True

def printprofile(input):
	access_file = input.config.get('svn', 'access_file')
	htpasswd = mod_htpasswd.HTPasswd(access_file)
	users = htpasswd.users()
	users.sort()

	posted_user = ''
	posted_change = False
	posted_remove = False
	posted_add = False
	if input.post.has_key('user'):
		posted_user = input.post['user']
	if input.post.has_key('change_user'):
		posted_change = True
	if input.post.has_key('remove_user'):
		posted_remove = True
	if input.post.has_key('add_user'):
		posted_add = True

	print '''
	<form name="" action="%s/users" method="post">
	<div class="container">
		<b>Change user</b>
		<div class="row">
			<label for="change_user">User:</label>
			<select class="form" name="user" id="user">
				<option value="">Choose a user</option> ''' % input.base

	for user in users:
		selected = ''
		if user == posted_user and (posted_remove or posted_change):
			selected = ' selected'

		print '<option value="%s"%s>%s</option>' % (user, selected, user)

	print '''
			</select>
		</div>
		<div class="row">
			<label for="password">New password:</label>
			<input class="form" type="password" name="password" value="" 
				id="password" />
		</div>
		<div class="row">
			<label for="password2">Again:</label>
			<input class="form" type="password" name="password2" value=""
				id="password2" />
		</div>'''

	print '''
		<div class="row">
			<label>&nbsp;</label>
			<input class="form" type="submit" name="change_user" 
				value="Change user" />
			<input class="form" type="submit" name="remove_user" 
				value="Remove user" />
		</div>
	</div>
	</form>
	'''

	posted_add_user = ''
	if posted_add:
		posted_add_user = posted_user

	print '''
	<form name="" action="%s/users" method="post">
	<div class="container">
		<b>Add user</b>
		<div class="row">
			<label for="user">User:</label>
			<input class="form" type="text" name="user" value="%s" id="user" />
		</div>
		<div class="row">
			<label for="add_password">Password:</label>
			<input class="form" type="password" name="password" value="" 
				id="add_password" />
		</div>
		<div class="row">
			<label for="add_password2">Again:</label>
			<input class="form" type="password" name="password2" value="" 
				id="add_password2" />
		</div>
		<div class="row">
			<label>&nbsp;</label>
			<input class="form" type="submit" name="add_user" 
				value="Add user" />
		</div>
	</div>
	</form>
	''' % (input.base, posted_add_user)

def handleinput(input):
	want_change = input.post.has_key('change_user')
	want_add = input.post.has_key('add_user')
	want_remove = input.post.has_key('remove_user')
	has_user = input.post.has_key('user')
	has_password = input.post.has_key('password') 
	has_password2 = input.post.has_key('password2') 

	if has_user and (want_change or want_add):
		if has_password and has_password2:
			password = input.post['password']
			password2 = input.post['password2']
			if password != password2:
				print '<p class="msg">Passwords do not match!</p>'
			else:
				if want_change:
					changepassword(input, input.post['user'], password)
				if want_add:
					adduser(input, input.post['user'], password)
		else:
			print '''<p class="msg">
				You need to fill in both password fields to do this</p>'''

	if has_user and want_remove:
		removeuser(input, input.post['user'])

	if (want_remove or want_add or want_change) and not has_user:
		print '<p class="msg">Which user do you want to '
		if want_remove:	print 'remove'
		if want_change:	print 'change'
		if want_add: print 'add'
		print '?</p>'

	printprofile(input)

def changepassword(input, user, password):
	if user is None:
		print '<p class="msg">Nobody is logged in!</p>'
		return

	access_file = input.config.get('svn', 'access_file')
	htpasswd = mod_htpasswd.HTPasswd(access_file)
	htpasswd.change(user, password)
	htpasswd.flush()
	print '<p class="msg">Password changed</p>'

def adduser(input, user, password):
	access_file = input.config.get('svn', 'access_file')
	htpasswd = mod_htpasswd.HTPasswd(access_file)
	if htpasswd.exists(user):
		print '<p class="msg">User ' + user + ' already exists</p>'
		return

	htpasswd.add(user, password)
	htpasswd.flush()
	print '<p class="msg">User ' + user + ' added</p>'

def removeuser(input, user):
	access_file = input.config.get('svn', 'access_file')
	htpasswd = mod_htpasswd.HTPasswd(access_file)
	if not htpasswd.exists(user):
		print '<p class="msg">User ' + user + ' doesn\'t exist</p>'
		return

	htpasswd.remove(user)
	htpasswd.flush()
	print '<p class="msg">' + user + ' removed</p>'

def handler(input):
	print input.html.header('users')

	handleinput(input)

	print input.html.footer()
