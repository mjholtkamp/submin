class User:
	class DoesNotExist(Exception):
		pass

	def __init__(self, config, name):
		self.name = name
		self.config = config

		authz_users = self.config.authz.users()
		htpasswd_users = self.config.htpasswd.users()

		if self.name not in htpasswd_users:
			raise User.DoesNotExist

		self.member_of = self.config.authz.member_of(self.name)

		self.email = ''
		if authz_users.has_key(self.name):
			if authz_users[self.name].has_key('email'):
				self.email = authz_users[self.name]['email']
	
	def __str__(self):
		return self.name
