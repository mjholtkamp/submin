#!/usr/bin/python

class Admin:
	def __init__(self):
		self.vars = {}
		self.vars['submin root'] = '/var/lib/submin/'
		self.vars['svn dir'] = 'svn'
		self.vars['trac dir'] = 'trac'

	def _path(self, path):
		if len(path) == 0 or path[0] == '/':
			return path

		return self.vars['submin root'] + path

	def _setpath(self, name, path):
		if path[-1:] != '/':
			path += '/'
		self.vars[name] = path

	def run(self, argv):
		if len(argv) < 2:
			self.c_help(argv)
			return

		try:
			command = getattr(self, 'c_' + argv[1])
			command(argv)
		except:
			print "Sorry, don't know command `%s', try help" % argv[1]
			raise

	def create_subminconf_from_template(self):
		vars = self.replacedvars()
		submin_conf = open('/usr/lib/submin/conf/submin.conf.example').read()
		submin_conf = submin_conf.replace('/var/lib/submin/svn', vars['svn dir'])
		submin_conf = submin_conf.replace('/var/lib/submin', vars['submin root'])
		submin_conf_file = vars['submin root'] + 'submin.conf'
		out = open(submin_conf_file, 'w')
		out.write(submin_conf)
		out.close()

	def c_create(self, argv):
		"""Create a new submin environment
create <submin-root> <svn-dir> [<trac-dir>]

	<submin-root>\t- submin data dir (default: %(submin root)s)
	\t\t  holds the files: htpasswd, authz, submin.conf
	<svn-dir>\t- svn repository dir (default: %(svn dir)s)
	<trac-dir>\t- trac projects dir (default: %(trac dir)s)
"""
		if len(argv) > 2:
			self._setpath('submin root', argv[2])
		if len(argv) > 3:
			self._setpath('svn dir', argv[3])
		if len(argv) < 4:
			self.vars['trac dir'] = ''

		vars = self.replacedvars()
		submin_conf_file = vars['submin root'] + 'submin.conf'

		# create dir
		import os
		os.mkdir(os.path.dirname(submin_conf_file))

		# make submin.conf
		self.create_subminconf_from_template()

		# add an admin user and submin-admin group
		from config.config import Config
		conf = Config(submin_conf_file)
		conf.htpasswd.add('admin', 'admin')
		conf.authz.addGroup('submin-admin', ['admin'])
		print 'created submin configuration with default user admin (password: admin)'

	def c_help(self, argv):
		"""This help (supply a command for more information)
help <command>"""

		if len(argv) < 3:
			self.usage(argv)
			return

		try:
			doc = self.getlongdescription('c_' + argv[2])
			vars = self.replacedvars()
			print "Usage: %s %s " % (argv[0], doc % vars)
		except:
			raise

	def replacedvars(self):
		vars = self.vars.copy()
		vars['svn dir'] = self._path(vars['svn dir'])
		vars['trac dir'] = self._path(vars['trac dir'])
		return vars

	def getshortdescription(self, command):
		doc = self.getdescription(command)
		if doc == None:
			return None
		return doc.split('\n', 1)[0]

	def getlongdescription(self, command):
		doc = self.getdescription(command)
		if doc == None:
			return None
		return doc.split('\n', 1)[1]

	def getdescription(self, command):
		try:
			method = getattr(self, command)
		except:
			return None

		return method.__doc__

	def usage(self, argv):
		commands = [x for x in dir(self) if x.startswith('c_')]
		commandstr = '<' + '|'.join(x[2:] for x in commands) + '>'
		print "Usage: %s %s" % (argv[0], commandstr)
		print
		for command in commands:
			c = command[2:]
			print "\t%10s - %s" % (c, self.getshortdescription(command))
		print

if __name__ == "__main__":
	from sys import argv, path
	path.append('/usr/lib/submin/lib')

	try:
		a = Admin()
		a.run(argv)
	except KeyboardInterrupt:
		print

