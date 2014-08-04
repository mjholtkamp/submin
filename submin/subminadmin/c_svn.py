from submin.plugins.vcs.svn.export import export_authz

class c_svn():
	'''Subversion commands
Usage:
    svn export authz
'''
	needs_env = True

	def __init__(self, sa, argv):
		self.sa = sa
		self.argv = argv

	def subcmd_authz(self, args):
		if len(args) < 1:
			self.sa.execute(['help', 'svn'])
			return False

		if args[0] == 'export':
			export_authz()
		else:
			self.sa.execute(['help', 'svn'])
			return False

		return True

	def run(self):
		if len(self.argv) < 1:
			self.sa.execute(['help', 'svn'])
			return False

		try:
			subcmd = getattr(self, 'subcmd_%s' % self.argv[0])
		except AttributeError:
			self.sa.execute(['help', 'svn'])
			return False

		return subcmd(self.argv[1:])
