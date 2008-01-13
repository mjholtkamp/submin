from config.config import Config
from config.authz.authz import UnknownMemberError, MemberExistsError, UnknownGroupError

def addGroup(groupname):
	config = Config()
	config.authz.addGroup(groupname)

class Group(object):
	def __init__(self, name):
		config = Config()

		self.name = name

		if self.name not in config.authz.groups():
			raise UnknownGroupError, self.name

		self.members = config.authz.members(self.name)
		self.members.sort()
		allusers = config.htpasswd.users()
		allusers.sort();
		self.nonmembers = [nonmember for nonmember in allusers if nonmember not
				in self.members]

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

	def addMember(self, member):
		"""Adds a member to this group.
		Returns True if succesful, False otherwise
		"""
		config = Config()
		try:
			config.authz.addMember(self.name, member)
			return True
		except MemberExistsError:
			return False

	def remove(self):
		config = Config()
		config.authz.removeGroup(self.name)

	def __str__(self):
		return self.name
