from submin.models.exceptions import StorageError

class c_help():
	'''Get a list of commands, or specific information on a command
Usage:
    help           - get a list of commands and it's use,
    help [command] - get more help on that command'''

	needs_env = False

	def __init__(self, sa, argv):
		self.sa = sa
		self.argv = argv

	def run(self):
		if len(self.argv) > 0:
			cmd = self.sa.cmd_alias(self.argv[0])
			try:
				instance = self.sa.cmd_instance(cmd, [])
			except StorageError:
				print "This module needs a submin environment to show help"
				return

			if instance:
				docs = instance.__doc__.split('\n', 1)
				print docs[1]
				print
			else:
				print "No help available on unknown command"
		else:
			print "Commands:"
			cmds = self.sa.commands()
			for cmd in cmds:
				try:
					instance = self.sa.cmd_instance(cmd, [], print_error=False)
				except StorageError:
					docs = " !!! ERROR: This module needs a submin environment"
				else:
					if instance is None:
						docs = "  !!! ERROR: module import failed !!!"
					elif instance.__doc__ is None:
						docs = "No help available"
					else:
						docs = instance.__doc__.split('\n', 1)[0]

				print "  %-10s - %s" % (cmd, docs)
			print """
Use 'help [command]' to get more information on that command
"""
