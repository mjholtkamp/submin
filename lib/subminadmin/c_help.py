class c_help():
	"""Provides help on commands and subcommands"""
	def __init__(self, sa, argv):
		self.sa = sa
		self.argv = argv

	def run(self):
		if len(self.argv) > 0:
			subject = self.sa.import_class(self.argv[0], [])
			if subject:
				print subject.__doc__
			else:
				print "No help available on unknown command"
		else:
			print "Usage: help [subcommand]"
			subcmds = self.sa.subcommands()
			for subcmd in subcmds:
				print subcmd
