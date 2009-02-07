class c_help():
	'''Get a list of commands, or specific information on a command
Usage:
    help           - get a list of commands and it's use,
    help [command] - get more help on that command'''

	def __init__(self, sa, argv):
		self.sa = sa
		self.argv = argv

	def run(self):
		if len(self.argv) > 0:
			cmd = self.sa.cmd_alias(self.argv[0])
			instance = self.sa.cmd_instance(cmd, [])
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
				instance = self.sa.cmd_instance(cmd, [])
				docs = instance.__doc__.split('\n', 1)
				print "%10s - %s" % (cmd, docs[0])
			print """
Use 'help [command]' to get more information on that command
"""
