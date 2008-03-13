#!/usr/bin/python

from path.path import Path

class SubminAdmin:
	def __init__(self):
		self.vars = {}
		self.vars['submin root'] = Path('/var/lib/submin/')
		self.vars['svn dir'] = Path('svn', absolute=False)
		self.vars['trac dir'] = Path('trac', absolute=False)
		self.vars['overwrite'] = False
		self.vars['etc'] = Path('/etc/submin')
		self.vars['apache user'] = ''

	def _path(self, path):
		if path.absolute:
			return path

		return self.vars['submin root'] + path

	def run(self, argv):
		if len(argv) < 2:
			self.c_help(argv)
			return

		try:
			command = getattr(self, 'c_' + argv[1])
			command(argv)
		except AttributeError:
			print "Sorry, don't know command `%s', try help" % argv[1]

	def generate_session_salt(self):
		import random
		salts = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789./'
		salt = ''
		rand = random.Random()
		for i in range(16):
			salt += rand.choice(salts)

		return salt

	def get_apache_user(self, preferred):
		from pwd import getpwnam
		users = []
		for user in [preferred, 'www-data', 'httpd', 'apache']:
			pwd = ()
			try:
				pwd = getpwnam(user)
			except KeyError, e:
				pass
			else:
				return pwd

		return

	def create_submin_conf_from_template(self):
		import os

		vars = self.replacedvars()
		vars['session salt'] = self.generate_session_salt()

		submin_conf = '''[svn]
authz_file = %(authz)s
userprop_file = %(userprop)s
access_file = %(htpasswd)s
repositories = %(svn dir)s

[www]
base_url = /submin

[generated]
session_salt = %(session salt)s
''' % vars

		file(vars['submin conf'], 'w').write(submin_conf)

		return True

	def create_apache_conf(self):
		# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/496889
		import sys, inspect, os
		vars = self.replacedvars()
		www_dir = os.path.dirname(inspect.getfile(sys._getframe(1)))
		www_dir = os.path.realpath(os.path.join(www_dir, '../../www'))
		vars['www dir'] = www_dir
		vars['REQ_FILENAME'] = '%{REQUEST_FILENAME}'; # hack :)

		apache_conf = '''
    Alias /submin %(www dir)s
    <Directory %(www dir)s>
        Options ExecCGI FollowSymLinks
        AddHandler cgi-script py cgi pl
        SetEnv SUBMIN_CONF %(submin conf)s

        RewriteEngine on
        RewriteBase /submin/

        RewriteCond %(REQ_FILENAME)s !-f
        RewriteRule ^(.+)$ submin.cgi/$1

        RewriteRule ^/?$ submin.cgi/
    </Directory>

    <Location /svn>
        DAV svn
        SVNParentPath %(svn dir)s

        AuthType Basic
        AuthName "Subversion repository"

        AuthUserFile %(htpasswd)s
        AuthzSVNAccessFile %(authz)s

        Satisfy Any
        Require valid-user
    </Location>

''' % vars

		file(vars['apache conf'], 'w').write(apache_conf)
		print '''
Apache file %s created.
Please include it in your apache.conf
''' % vars['apache conf']


	def c_create(self, argv):
		"""Create a new submin environment
create <name> [options]

	<name> = project name, used for some file names

options:
	-r, --submin-root <submin-root>
		Submin data dir (default: %(submin root)s)
		holds the files: htpasswd, authz, userproperties.conf
	-s, --svn-dir <svn-dir>
		Subversion repository dir (default: <submin-root>/%(svn dir)s)
	-t, --trac-dir <trac-dir>
		Trac projects dir (default: <submin-root>/%(trac dir)s)
		*** trac is not actually integrated yet! ***
	-e, --etc-dir <etc-dir>
		Submin configuarion dir for static config (default: %(etc)s)
		holds the files <name>.conf and <name>-apache.conf
	-a, --apache-user <username>
		Use this if submin-admin is unable to guess which user runs the
		webserver.
	-f, --force-overwrite
		if this is specified, existing installation is overwritten
"""
		from getopt import gnu_getopt, GetoptError
		import os

		shortopts = 'fr:s:t:e:a:'
		longopts = ['submin-root=', 'svn-dir=', 'trac-dir=', 'etc-dir=',
					'apache-user=', 'force-overwrite']

		options = []
		try:
			options, arguments = gnu_getopt(argv[2:], shortopts, longopts)
		except GetoptError, e:
			print e
			return

		for option, optarg in options:
			if option in ['--submin-root', '-r']:
				self.vars['submin root'] = Path(optarg)
			elif option in ['--svn-dir', '-s']:
				absolute = False
				if optarg[0] == '/':
					absolute = True
				self.vars['svn dir'] = Path(optarg, absolute=absolute)
			elif option in ['--trac-dir', '-t']:
				self.vars['trac dir'] = Path(optarg)
			elif option in ['--force-overwrite', '-f']:
				self.vars['overwrite'] = True
			elif option in ['--etc-dir', '-e']:
				self.vars['etc'] = Path(optarg)
			elif option in ['--apache-user', '-a']:
				self.vars['apache user'] = optarg

		if len(argv) < 3:
			self.c_help([argv[0], 'help', 'create'])
			return

		self.name = arguments[0]

		# See if we can guess who the apache user is
		apache = self.get_apache_user(self.vars['apache user'])
		if not apache:
			print '''
Unable to guess the username of the webserver, please provide the username with
the `--apache-user <username>' option
'''
			return

		self.vars['submin conf'] = self.vars['etc'] + self.name + '.conf'
		self.vars['apache conf'] = self.vars['etc'] + self.name + '-apache.conf'
		self.vars['htpasswd'] = self.vars['submin root'] + 'htpasswd'
		self.vars['authz'] = self.vars['submin root'] + 'svn.authz'
		self.vars['userprop'] = self.vars['submin root'] + 'userproperties.conf'
		vars = self.replacedvars()

		# don't bother checking if we force anyway
		if not vars['overwrite']:
			existing_installation = False
			for var in ['submin root', 'htpasswd', 'authz', 'userprop',
						'submin conf', 'apache conf']:
				if os.path.exists(str(vars[var])):
					print '%s already exists' % vars[var]
					existing_installation = True

			if existing_installation:
				if not vars['overwrite']:
					print
					print 'Existing installation found, aborting.'
					print 'Use --force-overwrite to install anyway.'
					return

		# create dirs
		for key in ['submin root', 'etc', 'svn dir']:
			dir = str(vars[key])
			if not os.path.exists(dir):
				try:
					os.makedirs(dir)
				except OSError:
					print 'making dir %s failed, do you have permissions?' % dir
					return

		# make submin.conf
		self.create_submin_conf_from_template()

		# create apache.conf
		self.create_apache_conf()

		# add an admin user and submin-admin group
		from config.config import Config
		from config.authz.authz import UnknownGroupError

		conf = Config(vars['submin conf'])
		conf.htpasswd.add('admin', 'admin')
		try:
			conf.authz.removeGroup('submin-admins') # on overwrite
		except UnknownGroupError:
			pass # ignore

		conf.authz.addGroup('submin-admins', ['admin'])

		# fix permissions
		for item in ['submin root', 'svn dir', 'authz', 'htpasswd', 'userprop']:
			s = str(vars[item])
			try:
				os.chown(s, apache.pw_uid, apache.pw_gid)

			except OSError:
				print ' *** Failed to change permissions of %s' % s
				print '     to apache user. Are you root?'


		print 'Created submin configuration with default user admin (password: admin)'

	def c_help(self, argv):
		"""This help (supply a command for more information)
help <command>"""

		if len(argv) < 3:
			self.usage(argv)
			return

		try:
			doc = self.getlongdescription('c_' + argv[2])
			print "Usage: %s %s " % (argv[0], doc % self.vars)
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
		commandstr = '<' + '|'.join([x[2:] for x in commands]) + '>'
		print "Usage: %s %s" % (argv[0], commandstr)
		print
		for command in commands:
			c = command[2:]
			print "\t%10s - %s" % (c, self.getshortdescription(command))
		print


