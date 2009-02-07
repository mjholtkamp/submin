import os

class c_initenv():
	'''Initialize a new enviroment
Usage:
    initenv
            -- Create environment interactively
    initenv <repospath>
            -- Create environment from arguments'''

	def __init__(self, sa, argv):
		self.sa = sa
		self.argv = argv
		self.defaults = {'svn dir': 'svn'}
		self.init_vars = {'conf dir': 'conf'}

	def prompt_user(self, prompt, default):
		defval = self.defaults[default]
		a = raw_input("%s [%s]> " % (prompt, defval))
		if a == '':
			return defval

		return a

	def interactive(self):
		svn_dir = self.prompt_user("Path to the repository", 'svn dir')
		self.init_vars['svn dir'] = svn_dir
		self.create_env()

	def create_dir(self, directory):
		"""Create a relative or absulute directory, if it doesn't exists already"""
		if not os.path.exists(directory):
			if directory[0] != os.path.sep:
				directory = os.path.join(self.sa.env, directory)
			os.makedirs(directory, mode=0700)

	def create_env(self):
		"""This is called when all info is gathered"""
		self.create_dir(self.sa.env)
		self.create_dir(self.init_vars['svn dir'])
		self.create_dir(self.init_vars['conf dir'])

	def run(self):
		if os.path.exists(self.sa.env):
			print "Directory already exists, won't overwrite"
			return

		if len(self.argv) < 1:
			self.interactive()
			return

		expected_args = 1
		if len(self.argv) != expected_args:
			print "Wrong number of arguments, expected: %u" % expected_args
			return

		self.init_vars['svn dir'] = self.argv[0]
		self.create_env()
