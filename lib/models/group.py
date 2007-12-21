from config.config import Config
from config.authz.authz import UnknownMemberError

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

	def removeMember(self, member):
		"""Removes a member from this group.
		Returns True if successful, False otherwise
		"""
		config = Config()
		try:
			config.authz.removeMember(self.name, member)
			return True
		except UnknownMemberError:
			return False

	def __str__(self):
		return self.name
