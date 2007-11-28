#!/usr/bin/python

class Admin:
	def __init__(self):
		self.commands = {}
		self.commands['create'] = ['Create a new submin environment',
			"""create <param1> <param2>"""]
		self.commands['help'] = ['This help (supply a command for more' +
			' information)', 'help <command>']

	def run(self, argv):
		if len(argv) < 2:
			a.help(argv)
			return

		try:
			command = getattr(self, argv[1])
			command(argv)
		except:
			self.usage(argv)

	def help(self, argv):
		if len(argv) < 3 or not self.commands.has_key(argv[2]):
			self.usage(argv)
			return

		print "Usage: %s %s " % (argv[0], self.commands[argv[2]][1])

	def usage(self, argv):
		commands = '<' + '|'.join(x for x in self.commands.iterkeys()) + '>'
		print "Usage: %s %s" % (argv[0], commands)
		print
		for command, description in self.commands.iteritems():
			print "\t%s\t- %s" % (command, description[0])
		print

if __name__ == "__main__":
	from sys import argv, path
	path.append('/usr/lib/submin/www/lib')

	try:
		a = Admin()
		a.run(argv)
	except KeyboardInterrupt:
		print

