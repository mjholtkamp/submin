import sys

class SubminAdmin:
	def __init__(self, argv):
		self.argv = argv
		self.prompt_fmt = "submin-admin [%s]> "
		self.prompt = ""
		self.quit = False

	def run(self):
		if len(self.argv) < 2:
			self.usage()
			return

		self.env = self.argv[1]
		self.prompt = self.prompt_fmt % self.env

		if len(self.argv) < 3:
			self.interactive()
			return

		self.execute(self.argv[2:])

	def interactive(self):
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
		import os
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

	def execute(self, argv):
		if len(argv) < 1:
			return True

		cmd = argv[0]
		Class = self.import_class(cmd, argv[1:])
		if not Class:
			print "Unknown command"
			return True

		return Class.run()

	def usage(self):
		print "Usage: %s </path/to/projenv> [command [subcommand] [option]]" \
				% self.argv[0]