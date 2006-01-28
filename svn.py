import ConfigParser

class Authz:
	def __init__(self, authz_file):
		self.authz_file = authz_file
		self.parser = ConfigParser.ConfigParser()
		self.parser.readfp(open(self.authz_file))

	def paths(self):
		sections = []
		for section in self.parser.sections():
			if section != 'groups':
				if section == '/':
					sections.append([None, '/'])
				else:
					sections.append(section.split(':', 1))
		return sections

	def currentPermissions(self, repository, path):
		if repository is not None:
			path = '%s:%s' % (repository, path)
		elif path != '/':
			return []

		return self.parser.items(path)

	def groups(self):
		try:
			return self.parser.options('groups')
		except ConfigParser.NoSectionError:
			return []

	def members(self, group):
		try:
			members = self.parser.get('groups', group).split(',')
			return [m.strip() for m in members]
		except ConfigParser.NoOptionError:
			return []

if __name__ == '__main__':
	tmp_conf = "/home/avaeq/public_html/submerge/submerge.conf"
	cp = ConfigParser.ConfigParser()
	cp.readfp(open(tmp_conf))

	authz_file = cp.get('svn', 'authz_file')

	authz = Authz(authz_file)

	print 'authz.paths()\n\t', authz.paths()
	repos, path = authz.paths()[-1]
	print 'permissions submerge:/\n\t', \
			authz.currentPermissions(repos, path)
	print 'permissions /\n\t', authz.currentPermissions(None, '/')
	print 'groups\n\t', authz.groups()
	print 'devel members\n\t', authz.members('devel')
	print 'foo members\n\t', authz.members('foo')
