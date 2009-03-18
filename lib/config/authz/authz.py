# -*- coding: utf-8 -*-
import ConfigParser

# Exceptions
class GroupExistsError(Exception):
	def __init__(self, group):
		Exception.__init__(self, 'Group %s already exists' % group)

class UnknownGroupError(Exception):
	def __init__(self, group):
		Exception.__init__(self, 'Group %s does not exist' % group)

class UnknownUserError(Exception):
	def __init__(self, user):
		Exception.__init__(self, 'User %s does not exist' % user)

class MemberExistsError(Exception):
	def __init__(self, user, group):
		Exception.__init__(self, 'User %s already exists in group %s' % (user, group))

class UnknownMemberError(Exception):
	def __init__(self, user, group):
		Exception.__init__(self, 'User %s is not member of group %s' % (user, group))

class InvalidUserError(Exception):
	def __init__(self, user):
		Exception.__init__(self, 'User `%s\' is invalid' % user)

class InvalidGroupError(Exception):
	def __init__(self, group):
		Exception.__init__(self, 'Group `%s\' is invalid' % group)

class InvalidRepositoryError(Exception):
	def __init__(self, repos, path):
		Exception.__init__(self, 'Repository %s does not exist (path: %s)' % (repos, path))

class PathExistsError(Exception):
	def __init__(self, repos, path):
		Exception.__init__(self, 'Path %s already exists in repository %s' % (path, repos))

class UnknownPathError(Exception):
	def __init__(self, repos, path):
		Exception.__init__(self, 'Path %s unknown in repository %s' % (path, repos))

class UnknownPermissionError(Exception):
	def __init__(self, path, name):
		Exception.__init__(self, 'Permission for %s does not exist in path %s' % (name, path))

class Authz:
	def __init__(self, authz_file, userprop_file):
		self.authz_file = authz_file
		self.userprop_file = userprop_file
		self.authzParser = ConfigParser.ConfigParser()
		self.userPropParser = ConfigParser.ConfigParser()
		try:
			self.authzParser.readfp(open(self.authz_file))
		except IOError:
			# make a new file
			open(self.authz_file, 'a')

		try:
			self.userPropParser.readfp(open(self.userprop_file))
		except IOError:
			# make a new file
			open(self.userprop_file, 'a')

		# Silently create groups section if it does not exist:
		if not self.authzParser.has_section('groups'):
			self.authzParser.add_section('groups')

	def save(self):
		"""Saves current authz configuration"""
		self.authzParser.write(open(self.authz_file, 'w+'))
		self.userPropParser.write(open(self.userprop_file, 'w+'))

	def paths(self, repository=None):
		"""Returns all the repository:path entries in the authz-file
		   if repository is given, returns only paths that belong to it."""
		from path.path import Path
		sections = []
		for section in self.authzParser.sections():
			if section != 'groups':
				if repository and not section.startswith(repository + ':'):
					pass
				elif section == '/':
					sections.append([None, '/'])
				elif section.startswith('user.'):
					# Legacy form of user.username in authz-file. Skip this.
					pass
				else:
					# Normalize paths
					s = section.split(':', 1)
					s[1] = str(Path(s[1], absolute=True))
					sections.append(s)
		return sections

	def users(self):
		users = {}
		for name in self.userPropParser.sections():
			properties = {}
			for option in self.userPropParser.options(name):
				properties[option] = self.userPropParser.get(name, option)
			users[name] = properties

		return users

	def userProp(self, user, property):
		if not self.userPropParser.has_section(user):
			raise UnknownUserError(user)

		return self.userPropParser.get(user, property)

	def setUserProp(self, user, property, value):
		if not self.userPropParser.has_section(user):
			self.userPropParser.add_section(user)

		self.userPropParser.set(user, property, value)
		self.save()

	def removeUserProps(self, user):
		self.userPropParser.remove_section(user)
		self.save()

	def createSectionName(self, repository, path):
		if repository is not None:
			path = '%s:%s' % (repository, path)
		elif path != '/':
			raise InvalidRepositoryError(repository, path)
		return path

	def removePath(self, repository, path):
		section = self.createSectionName(repository, path)
		self.authzParser.remove_section(section)
		self.save()

	def addPath(self, repository, path):
		section = self.createSectionName(repository, path)
		if section in self.authzParser.sections():
			raise PathExistsError(repository, path)
		self.authzParser.add_section(section)
		self.save()

	# Group methods
	def groups(self):
		"""Returns all the groups"""
		try:
			return self.authzParser.options('groups')
		except ConfigParser.NoSectionError:
			return []

	def members(self, group):
		"""Returns all the members for a group"""
		try:
			members = self.authzParser.get('groups', group).split(',')
			return [m.strip() for m in members if m.strip()]
		except ConfigParser.NoOptionError:
			raise UnknownGroupError(group)

	def member_of(self, user):
		member_groups = []
		for group in self.groups():
			if user in self.members(group):
				member_groups.append(group)
		return member_groups

	def addGroup(self, group, members=[]):
		"""Adds a group"""
		if group == '':
			raise InvalidUserError(group)
		if '' in members:
			raise InvalidUserError(member)
		if group in self.groups():
			raise GroupExistsError(group)
		self.authzParser.set('groups', group, ', '.join(members))
		self.save()

	def removeGroup(self, group):
		"""Removes a group"""
		if group not in self.groups():
			raise UnknownGroupError(group)
		self.authzParser.remove_option('groups', group)
		self.save()

	def addMember(self, group, member):
		"""Adds a member to a group"""
		if member == '':
			raise InvalidUserError(member)
		members = self.members(group)
		if member in members:
			raise MemberExistsError(member, group)
		members.append(member)
		self.authzParser.set('groups', group, ', '.join(members))
		self.save()

	def removeMember(self, group, member):
		"""Removes a member from a group"""
		if member == '':
			raise InvalidUserError(member)
		members = self.members(group)
		if member not in members:
			raise UnknownMemberError(member, group)
		members.remove(member)
		self.authzParser.set('groups', group, ', '.join(members))
		self.save()

	def removeAllMembers(self, group):
		"""Removes a member from a group"""
		if group not in self.groups():
			raise UnknownGroupError(group)
		self.authzParser.set('groups', group, '')
		self.save()

	def permissionDicts(self, path):
		dicts = []
		if not self.authzParser.has_section(path):
			(repos, dirpath) = path.split(':', 2)
			raise UnknownPathError(repos, dirpath)
		for tuple in self.authzParser.items(path):
			type = 'user'
			if tuple[0][0] == '@':
				type = 'group'

			dicts.append({'name': tuple[0][(type == 'group'):],
						'permission': tuple[1],
						'type': type})
		return dicts

	# Permission methods
	def permissions(self, repository, path, member=None):
		"""Returns the current permissions for the repository:path entry"""
		if repository is not None:
			path = '%s:%s' % (repository, path)
		elif path != '/':
			return []

		if member is None:
			try:
				dicts = self.permissionDicts(path)
			except UnknownPathError:
				return []
			return dicts

		return self.authzParser.get(path, member)

	def setPermission(self, repository, path, member, type, permission=''):
		"""Sets the permisson on repository:path for member.
		The type argument can be 'user' or 'group', if member == '*' then
		it matches all members."""
		if type == 'group':
			member = '@' + member

		path = path.encode('utf-8')
		section = self.createSectionName(repository, path)
		if not self.authzParser.has_section(section):
			self.authzParser.add_section(section)
		self.authzParser.set(section, member, permission)
		self.save()

	def removePermission(self, repository, path, member, type):
		"""Removes the members permission from the repository:path"""
		if type == 'group':
			member = '@' + member
		path = path.encode('utf-8')

		section = self.createSectionName(repository, path)
		retval = self.authzParser.remove_option(section, member)
		if not retval:
			raise UnknownPermissionError(section, member)

		if len(self.authzParser.items(section)) == 0:
			self.authzParser.remove_section(section)

		self.save()

	def removePermissions(self, member, type):
		'''Remove all permissions of user/group (defined by type), this is
		used when deleting a user/group'''
		paths = self.paths()
		for path in paths:
			repos = path[0]
			path = path[1]
			try:
				self.removePermission(repos, path, member, type)
			except UnknownPermissionError:
				pass # if it didn't exist, it's also fine
