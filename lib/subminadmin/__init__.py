import sys
import os

class SubminAdmin:
	def __init__(self, argv):
		self.argv = argv
		self.prompt_fmt = "Submin [%s]> "
		self.prompt = ""
		self.quit = False
		self.subcmd_aliases = [('?', 'help'), ('exit', 'quit')]

	def run(self):
		if len(self.argv) < 2:
			self.usage()
			return

		self.env = self.argv[1]
		if self.env[0] != os.path.sep:
			self.env = os.path.join(os.getcwd(), self.env)

		self.prompt = self.prompt_fmt % self.env

		if len(self.argv) < 3:
			self.interactive()
			return

		self.execute(self.argv[2:])

	def interactive(self):
		print '''Welcome to submin-admin
Interactive Submin administration console.

Use '?' or 'help' for help on commands.
'''
		while not self.quit:
			try:
				argv = raw_input(self.prompt).split()
			except (EOFError, KeyboardInterrupt):
				print
				return

			self.execute(argv)

	def import_class(self, cmd, argv):
		objname = "c_" + cmd
		try:
			fullobjname = "subminadmin." + objname
			X = __import__(fullobjname)
			Class = eval("X." + objname + "." + objname + "(self, argv)")
			return Class
		except ImportError, e:
			return None

	def subcommands(self):
		import glob
		import inspect
		import re

		basefile = inspect.getmodule(self).__file__
		basedir = os.path.dirname(basefile)
		pat = re.compile('c_(.*).py')
		subcmds = []
		for f in glob.glob('%s/c_*.py' % basedir):
			fname = os.path.basename(f)
			subcmd = re.search(pat, fname)
			subcmds.append(subcmd.group(1))

		return subcmds

	def subcmd_alias(self, subcmd):
		for tup in self.subcmd_aliases:
			if tup[0] == subcmd:
				return tup[1]

		return subcmd

	def execute(self, argv):
		if len(argv) < 1:
			return True

		cmd = self.subcmd_alias(argv[0])
		Class = self.import_class(cmd, argv[1:])
		if not Class:
			print "Unknown command"
			return True

		return Class.run()

	def usage(self):
		print "Usage: %s </path/to/projenv> [command [subcommand] [option]]" \
				% self.argv[0]