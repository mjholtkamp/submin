from lib.utils import mimport
mod_htpasswd = mimport('lib.htpasswd')

login_required = False

def printlogin(input):
	print '''
	<b>Please login</b><br />
	<form name="" action="%slogin" method="post">
	<div class="container">
		<div class="row">
			<label for="user">Username: </label>
			<input id="user" class="form" type="text" name="user" value="" tabindex="1" />
		</div>
		<div class="row">
			<label for="password">Password: </label>
			<input id="password" class="form" type="password" name="password" value="" tabindex="2" />
		</div>
		<div class="row">
			<label class="label">&nbsp;</label>
			<input class="form" type="submit" value="login" tabindex="3" />
		</div>
	</div>
	</form>
	''' % input.base

def login(input):
	user = input.post['user']
	password = input.post['password']
	access_file = input.config.get('svn', 'access_file')
	htpasswd = mod_htpasswd.HTPasswd(access_file)
	if htpasswd.check(user, password):
		input.saveSession(user)
		return True
	return False

def handler(input):
	# first handle login, than print header, because the header is 
	# dependent on the login-information
	newlogin = False
	loggedin = False
	if not input.isLoggedIn():
		if input.post.has_key('user') and input.post.has_key('password'):
			newlogin = True
			loggedin = login(input)

	print input.html.header('Main screen turn on')

	if newlogin:
		if loggedin:
			print 'Welcome %s' % input.session['user'] 
		else:
			print '<h2>Username or password incorrect</h2>'
			printlogin(input)
	else:
		if loggedin:
			print '''Hey %s, you are alread logged in :D<br />
				Perhaps you want to <a href="%slogout">logout</a>?
				''' % (input.session['user'], input.base)
		else:
			printlogin(input)

	print input.html.footer()
