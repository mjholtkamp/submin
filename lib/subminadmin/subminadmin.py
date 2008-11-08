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
		self.vars['http base'] = ''
		self.vars['share dir'] = '_SUBMIN_SHARE_DIR_'

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
		except AttributeError, e:
			print "Sorry, don't know command `%s', try help" % argv[1]
			return

		command(argv)

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
		# _www in OS X :)
		for user in [preferred, 'www-data', 'httpd', 'apache', '_www']:
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
base_url = %(http base)s/submin

[backend]
bindir = %(share dir)/bin

[generated]
session_salt = %(session salt)s
''' % vars

		file(str(vars['submin conf']), 'w').write(submin_conf)

		return True

	def create_apache_confs(self):
		# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/496889
		import sys, inspect, os
		vars = self.replacedvars()
		www_dir = os.path.dirname(inspect.getfile(sys._getframe(1)))
		www_dir = os.path.realpath(os.path.join(www_dir, '../../www'))
		vars['www dir'] = www_dir
		vars['REQ_FILENAME'] = '%{REQUEST_FILENAME}'; # hack :)

		apache_conf_cgi = '''
    Alias %(http base)s/submin %(www dir)s
    <Directory %(www dir)s>
        Order allow,deny
        Allow from all
        Options ExecCGI FollowSymLinks
        AddHandler cgi-script py cgi pl
        SetEnv SUBMIN_CONF %(submin conf)s

        RewriteEngine on
        RewriteBase %(http base)s/submin

        RewriteCond %(REQ_FILENAME)s !-f
        RewriteRule ^(.+)$ submin.cgi/$1

        RewriteRule ^/?$ submin.cgi/
    </Directory>

    <Location %(http base)s/svn>
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

		apache_conf_wsgi = '''
    WSGIScriptAlias %(http base)s/submin %(www dir)s/submin.wsgi
    AliasMatch ^%(http base)s/submin/css/(.*) %(www dir)s/css/$1
    AliasMatch ^%(http base)s/submin/img/(.*) %(www dir)s/img/$1
    AliasMatch ^%(http base)s/submin/js/(.*) %(www dir)s/js/$1

    <Location %(http base)s/submin>
        SetEnv SUBMIN_CONF %(submin conf)s
    </Location>

    <Location %(http base)s/svn>
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

		file(str(vars['apache conf cgi']), 'w').write(apache_conf_cgi)
		file(str(vars['apache conf wsgi']), 'w').write(apache_conf_wsgi)
		print '''
Apache files created:
   %(apache conf wsgi)s
   %(apache conf cgi)s

   Please include one of these in your apache config. Also make sure that
   you have mod_dav_svn and mod_authz_svn enabled.
''' % vars


	def c_create(self, argv):
		"""Create a new submin environment
create <name> [options]

Setup config files and create apache config. Also create password and user 
files and svn repository dir if not already present.

    <name> = Used for filenames in the static config dir (for example 'default')

options:
    -r, --submin-root <submin-root>
        Dynamic data dir (default: %(submin root)s), contains writable 
        files: htpasswd, authz, userproperties.conf and svn repository.
    --authz-file <file>
        Authz path (default: <submin-root>/authz).
    --htpasswd-file <file>
        Htpasswd path (default: <submin-root>/htpasswd).
    -e, --etc-dir <etc-dir>
        Static config dir (default: %(etc)s).
    -s, --svn-dir <svn-dir>
        Svn repository dir (default: <submin-root>/%(svn dir)s).
    -a, --apache-user <username>
        Specify which (http) user will own the dynamic data (default: guess).
    --http-base <base-path>
        Base path of the url for web access (default: '%(http base)s'). Submin and svn
        can be reached at: <base-path>/submin and <base-path>/svn.
    -f, --force-overwrite
        Overwrite existing installations without asking.
"""
# -t, --trac-dir <trac-dir>
#		Trac projects dir (default: <submin-root>/%(trac dir)s)
#		*** trac is not actually integrated yet! ***

		from getopt import gnu_getopt, GetoptError
		import os

		shortopts = 'fr:s:t:e:a:'
		longopts = ['submin-root=', 'authz-file=', 'htpasswd-file=',
					'svn-dir=', 'trac-dir=', 'etc-dir=', 'apache-user=',
					'http-base=', 'force-overwrite']

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
			elif option in ['--authz-file']:
				self.vars['authz'] = optarg
			elif option in ['--htpasswd-file']:
				self.vars['htpasswd'] = optarg
			elif option in ['--http-base']:
				self.vars['http base'] = optarg

		if len(argv) < 3:
			self.c_help([argv[0], 'help', 'create'])
			return

		if len(arguments) != 1:
			print "\nError: Please provide a project name as well\n"
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

		self.vars['submin conf'] = self.vars['etc'] + (self.name + '.conf')
		self.vars['apache conf cgi'] = self.vars['etc'] + (self.name + '-apache-cgi.conf')
		self.vars['apache conf wsgi'] = self.vars['etc'] + (self.name + '-apache-wsgi.conf')
		if 'htpasswd' not in self.vars:
			self.vars['htpasswd'] = self.vars['submin root'] + 'htpasswd'
		if 'authz' not in self.vars:
			self.vars['authz'] = self.vars['submin root'] + 'authz'

		self.vars['userprop'] = self.vars['submin root'] + 'userproperties.conf'
		vars = self.replacedvars()

		# don't bother checking if we force anyway
		if not vars['overwrite']:
			existing_installation = False
			for var in ['submin root', 'htpasswd', 'authz', 'userprop',
						'submin conf', 'apache conf cgi', 'apache conf wsgi']:
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
		self.create_apache_confs()

		# add an admin user and submin-admin group
		from config.config import Config
		from config.authz.authz import UnknownGroupError

		conf = Config(str(vars['submin conf']))
		conf.htpasswd.add('admin', 'admin')
		try:
			conf.authz.removeGroup('submin-admins') # on overwrite
		except UnknownGroupError:
			pass # ignore

		conf.authz.addGroup('submin-admins', ['admin'])

		# fix permissions/ownerships
		for item in ['submin root', 'svn dir', 'authz', 'htpasswd', 'userprop']:
			s = str(vars[item])
			try:
				if os.path.isdir(s):
					os.chmod(s, 0750)
				else:
					os.chmod(s, 0640)

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


