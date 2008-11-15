from config.config import Config
from config.authz.authz import UnknownMemberError, MemberExistsError, UnknownGroupError

def addGroup(groupname):
	config = Config()
	config.authz.addGroup(groupname)

def listGroups(is_admin):
	config = Config()
	groups = []
	authz_groups = config.authz.groups()
	authz_groups.sort()

	# make sure submin-admins is in front (it's special!)
	special_group = 'submin-admins'
	if special_group in authz_groups:
		authz_groups.remove(special_group)
		authz_groups.insert(0, special_group)

	for groupname in authz_groups:
		group = Group(groupname)
		if is_admin or session_user.name in group.members:
			groups.append(group)
	return groups

class Group(object):
	def __init__(self, name):
		config = Config()

		self.name = name

		if self.name not in config.authz.groups():
			raise UnknownGroupError(self.name)

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
