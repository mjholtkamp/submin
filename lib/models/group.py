from config.config import Config

class Group(object):
	class DoesNotExist(Exception):
		pass

	def __init__(self, name):
		config = Config()

		self.name = name

		if self.name not in config.authz.groups():
			raise Group.DoesNotExist

		self.members = config.authz.members(self.name)
		self.members.sort()

	def __str__(self):
		return self.name
