from config.config import Config
from ConfigParser import NoOptionError
from config.authz.authz import UnknownUserError

class UserExists(Exception):
	def __init__(self, user):
		Exception.__init__(self, 'User %s already exists' % user)

class NotAuthorized(Exception):
	def __init__(self, msg):
		Exception.__init__(self, msg)

class InvalidEmail(Exception):
	def __init__(self):
		Exception.__init__(self, "Invalid email")

class InvalidFullName(Exception):
	def __init__(self):
		Exception.__init__(self, "Invalid characters found in full name")

def listUsers(is_admin):
	config = Config()
	users = []
	htpasswd_users = config.htpasswd.users()
	htpasswd_users.sort()
	if is_admin:
		for user in htpasswd_users:
			try:
				users.append(User(user))
			except UnknownUserError:
				pass
	else:
		users.append(session_user)
	return users

def addUser(username):
	config = Config()
	if config.htpasswd.exists(username):
		raise UserExists(username)

	# generate a random password
	from string import ascii_letters, digits
	import random
	password_chars = ascii_letters + digits
	password = ''.join([random.choice(password_chars) for x in range(0, 50)])

	config.htpasswd.add(username, password)

def isEmailValid(email):
	import re
	# regex for quick email check. No quotes allowed, be very allowing
	# for domain-names and ip-addresses.
	regex = '^[^\'"@]+@(([\w-]\.?)+)$'
	email_check = re.compile(regex)
	if not email_check.match(email):
		return False
	return True

def isFullNameValid(fullname):
	import re
	# regex for quick fullname check. No quotes or newlines allowed.
	regex = '[\'"\n]'
	fullname_check = re.compile(regex)
	if fullname_check.search(fullname):
		return False
	return True


class User(object):
	def __init__(self, name):
		config = Config()

		self.name = name
		self.is_authenticated = False

		authz_users = config.authz.users()
		htpasswd_users = config.htpasswd.users()

		if self.name not in htpasswd_users:
			raise UnknownUserError(self.name)

		self.member_of = config.authz.member_of(self.name)
		self.nonmember_of = [nonmember_of for nonmember_of in
				config.authz.groups() if nonmember_of not in self.member_of]

		self.is_admin = 'submin-admins' in self.member_of

		self.__email = ''
		self.__fullname = ''
		if authz_users.has_key(self.name):
			if authz_users[self.name].has_key('email'):
				self.__email = authz_users[self.name]['email']
			if authz_users[self.name].has_key('fullname'):
				self.__fullname = authz_users[self.name]['fullname']
		

		# build notifications
		allowed = []
		enabled = []
		try:
			allowed = config.authz.userProp(self.name, 'notifications_allowed')
			allowed = [x.strip() for x in allowed.split(',')]
			enabled = config.authz.userProp(self.name, 'notifications_enabled')
			enabled = [x.strip() for x in enabled.split(',')]
		except (NoOptionError, UnknownUserError):
			pass
		
		self.notifications = {}
		repositories = config.repositories()
		for k in allowed:
			try:
				repositories.remove(k)
			except ValueError:
				continue
			enable = False
			if k in enabled:
				enable = True

			self.notifications[k] = dict(allowed=True,enabled=enable)

		for k in repositories:
			self.notifications[k] = dict(allowed=False,enabled=False)

	def __str__(self):
		return self.name

	def setNotification(self, name, notification, is_admin):
		# is_admin represents caller, not self.is_admin, which represents
		# this User object!!!
		if not is_admin and not self.notifications.has_key(name):
			raise NotAuthorized("You're not allowed to create permissions")
		
		if is_admin:
			# don't check, just set
			self.notifications[name] = dict(allowed=notification['allowed'],
				enabled=notification['enabled'])
			return

		# we know the key exists, see above checks
		old_notification = self.notifications[name]
		if not old_notification['allowed']:
			raise NotAuthorized("You're not allowed to change that notification")
		
		self.notifications[name] = dict(allowed=notification['allowed'],
			enabled=notification['enabled'])

	def saveNotifications(self):
		config = Config()
		
		allowed = []
		enabled = []
		for item in self.notifications.iteritems():
			if item[1]['allowed']:
				allowed.append(item[0])
			if item[1]['enabled']:
				enabled.append(item[0])
		
		config.authz.setUserProp(self.name, 'notifications_allowed', ', '.join(allowed))
		config.authz.setUserProp(self.name, 'notifications_enabled', ', '.join(enabled))
		config.authz.save()
		config.reinit()

	def getFullName(self):
		return self.__fullname
	
	def setFullName(self, fullname):
		if not isFullNameValid(fullname):
			raise InvalidFullName()

		self.__fullname = fullname
		config = Config()
		config.authz.setUserProp(self.name, 'fullname', fullname)
	fullname = property(getFullName, setFullName)
	
	def getEmail(self):
		return self.__email
		
	def setEmail(self, email):
		if not isEmailValid(email):
			raise InvalidEmail()
 
		self.__email = email
		config = Config()
		config.authz.setUserProp(self.name, 'email', email)
	email = property(getEmail, setEmail)

	def setPassword(self, password):
		config = Config()
		config.htpasswd.change(self.name, password)
		config.htpasswd.flush()
	password = property(fset=setPassword)

	def remove(self):
		config = Config()
		self.removeFromGroups(config) # pass config, otherwise next line will overwrite changes
		config.authz.removeUserProps(self.name)
		config.htpasswd.remove(self.name)
		config.htpasswd.flush()

	def removeFromGroups(self, config):
		for group in config.authz.groups():
			if self.name in config.authz.members(group):
				config.authz.removeMember(group, self.name)

