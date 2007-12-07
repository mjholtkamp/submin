from config.config import Config

class User:
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
	
	def __str__(self):
		return self.name
	
	
	def getEmail(self):
		return self.__email

	def setEmail(self, email):
		config = Config()
		config.authz.setUserProp(self.name, 'email', email)
	
	email = property(getEmail, setEmail)
