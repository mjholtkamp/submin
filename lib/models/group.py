class Group:
	class DoesNotExist(Exception):
		pass

	def __init__(self, config, name):
		self.name = name
		self.config = config

		if self.name not in config.authz.groups():
			raise DoesNotExist

		self.members = self.config.authz.members(self.name)
		self.members.sort()

	def __str__(self):
		return self.name
