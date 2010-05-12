import os
import sys
from submin.subminadmin import git

ERROR_STR = "submin-admin git is not supposed to be called by users."

def die():
	print >>sys.stderr, ERROR_STR
	sys.exit(1)

class c_git:
	# No doc-string to suppress the git-commands of showing up in the help
	# text.
	# - submin-admin <env> git user <username>
	#           -- to be called when trying to receive or upload a pack via
	#              ssh. Typically located in the command="" in the
	#              authorized_keys
	# - submin-admin <env> git admin
	#           -- to be called via ssh by the web interface to create a
	#              repository with the correct git-user permissions. The
	#              SSH_ORIGINAL_COMMAND can have two commands:
	#              - create <repo>
	#              - update-auth

	def __init__(self, sa, argv):
		self.sa = sa
		self.argv = argv

	def subcmd_user(self, args):
		if len(args) < 1:
			die()
		git.user.run(args[0])

	def subcmd_admin(self, args):
		if 'SSH_ORIGINAL_COMMAND' not in os.environ:
			die()
		cmd = os.environ['SSH_ORIGINAL_COMMAND']

		if cmd.startswith('create '):
			_, repo = cmd.split(' ', 1)
			repo = repo.strip()
			if not repo or ' ' in repo:
				die()
			git.create.run(repo)
		elif cmd == 'update-auth':
			git.update.run()
		else:
			die()

	def run(self):
		if len(self.argv) < 1:
			die()

		try:
			subcmd = getattr(self, 'subcmd_%s' % self.argv[0])
		except AttributeError:
			die()

		subcmd(self.argv[1:])
