import ConfigParser

# Exceptions
class GroupExistsError(Exception):
	def __init__(self, group):
		Exception.args = 'Group %s already exists' % group

class UnknownGroupError(Exception):
	def __init__(self, ):
		Exception.args = 'Group %s does not exist' % group

class UnknownUserError(Exception):
	def __init__(self, user):
		Exception.args = 'User %s does not exist' % user

class MemberExistsError(Exception):
	def __init__(self, user, group):
		Exception.args = 'User %s already exists in group %s' % (user, group)

class UnknownMemberError(Exception):
	def __init__(self, user, group):
		Exception.args = 'User %s is not member of group %s' % (user, group)

class InvalidRepositoryError(Exception):
	def __init__(self, repos, path):
		Exception.args = 'Repository %s does not exist (path: %s)' % (repos, path)

class PathExistsError(Exception):
	def __init__(self, repos, path):
		Exception.args = 'Path %s already exists in repositor %s' % (path, repos)


class Authz:
	def __init__(self, authz_file):
		self.authz_file = authz_file
		self.parser = ConfigParser.ConfigParser()
		self.parser.readfp(open(self.authz_file))

		# Silently create groups section if it does not exist:
		if not self.parser.has_section('groups'):
			self.parser.add_section('groups')

	def save(self):
		"""Saves current authz configuration"""
		self.parser.write(open(self.authz_file, 'w+'))

	def paths(self, repository=None):
		"""Returns all the repository:path entries in the authz-file
		   if repository is given, returns only paths that belong to it."""
		sections = []
		for section in self.parser.sections():
			if section != 'groups':
				if repository and not section.startswith(repository + ':'):
					pass
				elif section == '/':
					sections.append([None, '/'])
				elif section.startswith('user.'):
					pass
				else:
					sections.append(section.split(':', 1))
		return sections

	def users(self):
		users = {}
		for section in self.parser.sections():
			if section.startswith('user.'):
				name = section[5:]
				properties = {}
				for option in self.parser.options(section):
					properties[option] = self.parser.get(section, option)
				users[name] = properties

		return users

	def userProp(self, user, property):
		if not self.parser.has_section('user.' + user):
			raise UnknownUserError, user

		return self.parser.get('user.' + user, property)

	def setUserProp(self, user, property, value):
		if not self.parser.has_section('user.' + user):
			self.parser.add_section('user.' + user)

		self.parser.set('user.' + user, property, value)
		self.save()

	def removeUserProps(self, user):
		self.parser.remove_section('user.' + user)
		self.save()

	def createSectionName(self, repository, path):
		if repository is not None:
			path = '%s:%s' % (repository, path)
		elif path != '/':
			raise InvalidRepositoryError, (repository, path)
		return path


	def removePath(self, repository, path):
		section = self.createSectionName(repository, path)
		self.parser.remove_section(section)
		self.save()

	def addPath(self, repository, path):
		section = self.createSectionName(repository, path)
		if section in self.parser.sections():
			raise PathExistsError, (repository, path)
		self.parser.add_section(section)
		self.save()

	# Group methods
	def groups(self):
		"""Returns all the groups"""
		try:
			return self.parser.options('groups')
		except ConfigParser.NoSectionError:
			return []

	def members(self, group):
		"""Returns all the members for a group"""
		try:
			members = self.parser.get('groups', group).split(',')
			return [m.strip() for m in members if m.strip()]
		except ConfigParser.NoOptionError:
			raise UnknownGroupError, group

	def member_of(self, user):
		member_groups = []
		for group in self.groups():
			if user in self.members(group):
				member_groups.append(group)
		return member_groups

	def addGroup(self, group, members=[]):
		"""Adds a group"""
		if group in self.groups():
			raise GroupExistsError, group
		self.parser.set('groups', group, ', '.join(members))
		self.save()

	def removeGroup(self, group):
		"""Removes a group"""
		if group not in self.groups():
			raise UnknownGroupError, group
		self.parser.remove_option('groups', group)
		self.save()

	def addMember(self, group, member):
		"""Adds a member to a group"""
		members = self.members(group)
		if member in members:
			raise MemberExistsError, (member, group)
		members.append(member)
		self.parser.set('groups', group, ', '.join(members))
		self.save()

	def removeMember(self, group, member):
		"""Removes a member from a group"""
		members = self.members(group)
		if member not in members:
			raise UnknownMemberError, (member, group)
		members.remove(member)
		self.parser.set('groups', group, ', '.join(members))
		self.save()

	def removeAllMembers(self, group):
		"""Removes a member from a group"""
		if group not in self.groups():
			raise UnknownGroupError, group
		self.parser.set('groups', group, '')
		self.save()

	# Permission methods
	def permissions(self, repository, path, member=None):
		"""Returns the current permissions for the repository:path entry"""
		if repository is not None:
			path = '%s:%s' % (repository, path)
		elif path != '/':
			return []

		if member is None:
			return self.parser.items(path)

		return self.parser.get(path, member)

	def setPermission(self, repository, path, member, permission=''):
		"""Sets the permisson on repository:path for member.
		If member starts with a '@' it is a group, if member == '*' then
		it matches all members."""

		section = self.createSectionName(repository, path)
		if not self.parser.has_section(section):
			self.parser.add_section(section)
		self.parser.set(section, member, permission)
		self.save()

	def removePermission(self, repository, path, member):
		"""Removes the members permission from the repository:path"""
		section = self.createSectionName(repository, path)
		retval = self.parser.remove_option(section, member)
		if not retval:
			raise UnknownMemberError, (section, member)
		self.save()


if __name__ == '__main__':
	import sys
	if len(sys.argv) != 2:
		raise Exception, 'Please specify authz-file!'

	authz = Authz(sys.argv[1])

	# "tests"
	print 'authz.paths()\n\t', authz.paths()
	repos, path = authz.paths()[-1]
	print 'permissions submin:/\n\t', \
			authz.permissions(repos, path)
	print 'permissions /\n\t', authz.permissions(None, '/')
	print 'groups\n\t', authz.groups()
	try:
		print 'devel members\n\t', authz.members('devel')
	except UnknownGroupError: pass
	try:
		authz.removeGroup('foo')
	except UnknownGroupError: pass
	authz.addGroup('foo', ['avaeq'])
	print 'foo members\n\t', authz.members('foo')
	authz.addMember('foo', 'sabre2th')
	print 'foo members\n\t', authz.members('foo')
	authz.removeMember('foo', 'avaeq')
	print 'foo members\n\t', authz.members('foo')

	authz.setPermission('foo', '/', 'avaeq', 'r')
	print 'permissions foo:/\n\t', \
			authz.permissions('foo', '/')

	try:
		authz.addGroup('foo')
	except GroupExistsError, e:
		print 'Group already exists:', e

	try:
		authz.removeGroup('bar')
	except UnknownGroupError, e:
		print 'Unknown group:', e

	try:
		authz.addMember('foo', 'sabre2th')
	except MemberExistsError, e:
		print 'Member exists:', e

	try:
		authz.removeMember('foo', 'avaeq')
	except UnknownMemberError, e:
		print 'Unknown member:', e

	print 'users', authz.users()

