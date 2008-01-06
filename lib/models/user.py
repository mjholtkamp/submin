from config.config import Config
from ConfigParser import NoOptionError
from config.authz.authz import UnknownUserError

class UserExists(Exception):
	def __init__(self, user):
		Exception.args = 'User %s already exists' % user

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
		if authz_users.has_key(self.name):
			if authz_users[self.name].has_key('email'):
				self.__email = authz_users[self.name]['email']

		# build notifications
		allowed = []
		enabled = []
		try:
			allowed = config.authz.userProp(self.name, 'notifications_allowed')
			allowed = allowed.split(', ')
			enabled = config.authz.userProp(self.name, 'notifications_enabled')
			enabled = enabled.split(', ')
		except (NoOptionError, UnknownUserError):
			pass

		self.notifications = []
		for k in allowed:
			enable = False
			if k in enabled:
				enable = True

			self.notifications.append(dict(name=k,allowed=True,enabled=enable))

	def __str__(self):
		return self.name

	def getEmail(self):
		return self.__email

	def setEmail(self, email):
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

