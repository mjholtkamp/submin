import os
from path.path import Path
from config.authz.authz import UnknownGroupError

class c_initenv():
	'''Initialize a new enviroment
Usage:
    initenv                        - Create environment interactively
    initenv <repospath> <httpbase> - Create environment from arguments

Examples:
    initenv svn /
            -- Uses default repositories inside submin dir, submin website is
               reached at: http://example.com/submin
    initenv svn /dev
            -- As above, but site is reached at http://example.com/dev/submin
    initenv /var/lib/svn /
            -- Uses subversion repositories outside submin dir. If the
               directory doesn't already exist, it is created.'''

	def __init__(self, sa, argv):
		self.sa = sa
		self.env = Path(self.sa.env)
		self.argv = argv
		self.defaults = {
			'svn dir': Path('svn'),
			'http base': Path('/')
		}
		self.init_vars = {
			'conf dir': Path('conf'),
			'authz': Path('authz'),
			'htpasswd': Path('htpasswd')
		}

	def prompt_user(self, prompt, default):
		defval = self.defaults[default]
		a = raw_input("%s [%s]> " % (prompt, defval))
		if a == '':
			return defval

		p = Path(a)
		if type(p) == type(defval):
			return p

		return a

	def interactive(self):
		svn_dir = self.prompt_user("Path to the repository", 'svn dir')
		self.init_vars['svn dir'] = svn_dir
		http_base = self.prompt_user("HTTP base", 'http base')
		self.init_vars['http base'] = http_base
		self.create_env()

	def create_dir(self, directory):
		"""Create a relative or absulute directory, if it doesn't exist already"""
		if not os.path.exists(str(directory)):
			if not directory.absolute:
				directory = self.env + directory
			
			try:
				os.makedirs(str(directory), mode=0700)
			except OSError, e:
				print 'making dir %s failed, do you have permissions?' % \
						str(directory)
				raise e

	def create_env(self):
		"""This is called when all info is gathered"""
		try:
			self.create_dir(self.env)
			self.create_dir(self.init_vars['svn dir'])
			self.create_dir(self.init_vars['conf dir'])
		except OSError:
			return # already printed error message

		self.sa.execute(['config', 'defaults'])

		# write changes to config
		from config.config import Config
		os.environ['SUBMIN_ENV'] = self.sa.env
		c = Config()
		c.set('svn', 'repositories', str(self.init_vars['svn dir']))
		p = self.init_vars['http base']
		c.set('www', 'base_url', str(p + 'submin'))
		c.set('www', 'trac_base_url', str(p + 'trac'))
		c.set('www', 'svn_base_url', str(p + 'svn'))
		c.save()

		# add an admin user
		c.htpasswd.add('admin', 'admin')
		try:
			c.authz.removeGroup('submin-admins') # on overwrite
		except UnknownGroupError:
			pass # ignore

		c.authz.addGroup('submin-admins', ['admin'])
		print "\nAdded an admin user with password 'admin'\n"

	def run(self):
		if os.path.exists(str(self.env)):
			print "Directory already exists, won't overwrite"
			return

		if len(self.argv) < 1:
			self.interactive()
			return

		if len(self.argv) != 2:
			self.sa.execute(['help', 'initenv'])
			return

		self.init_vars['svn dir'] = Path(self.argv[0])
		self.init_vars['http base'] = Path(self.argv[1])
		self.create_env()
