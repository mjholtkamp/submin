from submin.subminadmin import git

class c_git:
	# No doc-string to suppress the git-commands of showing up in the help
	# text.
	# - submin-admin <env> git user <username>
	#           -- to be called when trying to receive or upload a pack via
	#              ssh. Typically located in the command="" in the
	#              authorized_keys
	# - submin-admin <env> git admin create <repo>
	#           -- to be called via ssh by the web interface to create a
	#              repository with the correct git-user permissions
	# - submin-admin <env> git admin update-auth
	#           -- to be called via ssh by the web interface to update the
	#              .ssh/authorized_keys file

	def __init__(self, sa, argv):
		self.sa = sa
		self.argv = argv

	def subcmd_user(self, args):
		if len(args) < 1:
			print "submin-admin git is not supposed to be called by users."
			return
		git.user.run(args[0])

	def run(self):
		if len(self.argv) < 1:
			print "submin-admin git is not supposed to be called by users."
			return

		try:
			subcmd = getattr(self, 'subcmd_%s' % self.argv[0])
		except AttributeError:
			print "submin-admin git is not supposed to be called by users."
			return

		subcmd(self.argv[1:])
