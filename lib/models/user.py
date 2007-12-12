from config.config import Config
from ConfigParser import NoOptionError
from config.authz.authz import UnknownUserError

class User(object):
	class DoesNotExist(Exception):
		pass

	def __init__(self, name):
		config = Config()

		self.name = name
		self.is_authenticated = False

		authz_users = config.authz.users()
		htpasswd_users = config.htpasswd.users()

		if self.name not in htpasswd_users:
			raise User.DoesNotExist

		self.member_of = config.authz.member_of(self.name)

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

	def getPassword(self):
		return '***'

	def setPassword(self, password):
		config = Config()
		config.htpasswd.change(self.name, password)
		config.htpasswd.flush()
	password = property(getPassword, setPassword)

