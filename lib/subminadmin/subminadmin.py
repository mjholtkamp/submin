#!/usr/bin/python

class SubminAdmin:
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

	def generate_session_salt(self):
		import random
		salts = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789./'
		salt = ''
		rand = random.Random()
		for i in range(16):
			salt += rand.choice(salts)

		return salt

	def get_apache_users(self):
		from pwd import getpwnam
		users = []
		for user in ['www-data', 'httpd', 'apache']:
			pwd = ()
			try:
				pwd = getpwnam(user)
			except KeyError, e:
				pass
			else:
				users.append(pwd)

		return users

	def create_subminconf_from_template(self, submin_conf_file):
		import os

		vars = self.replacedvars()
		self.authz_file = vars['submin root'] + 'svn.authz'
		self.userprop_file = vars['submin root'] + 'userproperties.conf'
		self.access_file = vars['submin root'] + 'htpasswd'
		self.repositories = vars['svn dir']
		session_salt = self.generate_session_salt()

		# bail if one of these things exists
		if os.path.exists(submin_conf_file):
			return False
		if os.path.exists(self.authz_file):
			return False
		if os.path.exists(self.userprop_file):
			return False
		if os.path.exists(self.access_file):
			return False
		if os.path.exists(self.repositories):
			return False

		submin_conf = '''[svn]
authz_file = %s
userprop_file = %s
access_file = %s
repositories = %s

[www]
media_url = /submin

[generated]
session_salt = %s
''' % (self.authz_file, self.userprop_file, self.access_file,
			self.repositories, session_salt)

		out = open(submin_conf_file, 'w')
		out.write(submin_conf)
		out.close()

		return True

	def create_apache_conf(self, submin_conf_file):
		vars = {'submin_config': submin_conf_file,
				'REQ_FILENAME': '%{REQUEST_FILENAME}',
				'www dir': '/usr/share/submin/www/',
				'htpasswd file': self.access_file,
				'authz file': self.authz_file,
				'svn dir': self.repositories}

		apache_conf = '''
    Alias /submin/ %(www dir)s
    <Directory %(www dir)s>
        Options ExecCGI FollowSymLinks
        AddHandler cgi-script py cgi pl
        SetEnv SUBMIN_CONF %(submin_config)s

        RewriteEngine on
        RewriteBase /submin/

        RewriteCond %(REQ_FILENAME)s !-f
        RewriteRule ^(.+)$ submin.py/$1

        RewriteRule ^/?$ submin.py/
    </Directory>

    <Location /svn>
        DAV svn
        SVNParentPath %(svn dir)s

        AuthType Basic
        AuthName "Subversion repository"

        AuthUserFile %(htpasswd file)s
        AuthzSVNAccessFile %(authz file)s

        Satisfy Any
        Require valid-user
    </Location>

''' % vars

		apache_conf_file = submin_conf_file.replace('.conf', '-apache.conf')

		import os
		if (os.path.exists(apache_conf_file)):
			backup = apache_conf_file + '.submin-backup'
			os.rename(apache_conf_file, backup)
			print 'Apache config file found, renamed to %s' % backup

		file(apache_conf_file, 'w').write(apache_conf)
		print 'Apache file %s created, please include it in your apache.conf' \
			% apache_conf_file


	def c_create(self, argv):
		"""Create a new submin environment
create <name> [<submin-root> [<svn-dir> [<trac-dir>]]]

	<name>\t\t- project name, defines some file names
	<submin-root>\t- submin data dir (default: %(submin root)s)
	\t\t  holds the files: htpasswd, authz,
	\t\t  userproperties.conf, submin.conf
	<svn-dir>\t- svn repository dir (default: <submin-root>/%(svn dir)s)
	<trac-dir>\t- trac projects dir (default: <submin-root>/%(trac dir)s)
"""
		if len(argv) < 3:
			self.c_help([argv[0], 'help', 'create'])
			return

		self.name = argv[2]
		if len(argv) > 3:
			self._setpath('submin root', argv[3])
		if len(argv) > 4:
			self._setpath('svn dir', argv[4])
		if len(argv) < 5:
			self.vars['trac dir'] = ''

		vars = self.replacedvars()
		submin_conf_file = '/etc/submin/' + self.name + '.conf'

		# create dir
		import os
		conf_dir = os.path.dirname(submin_conf_file)
		if not os.path.isdir(conf_dir):
			try:
				os.mkdir(conf_dir)
			except OSError:
				print 'making config dir failed, are you root?'
				return

		root_dir = vars['submin root']
		if not os.path.isdir(root_dir):
			try:
				os.mkdir(root_dir)
			except OSError:
				print 'Failed making submin root dir, do you have permissions?'
				return

		# make submin.conf
		if not self.create_subminconf_from_template(submin_conf_file):
			print 'previous installation (partly) available, aborting'
			return False

		# add an admin user and submin-admin group
		from config.config import Config
		conf = Config(submin_conf_file)
		conf.htpasswd.add('admin', 'admin')
		conf.authz.addGroup('submin-admins', ['admin'])

		os.mkdir(self.repositories)

		# fix permissions
		apache = self.get_apache_users()[0]
		try:
			os.chown(self.vars['submin root'], apache.pw_uid, apache.pw_gid)
			os.chown(self.repositories, apache.pw_uid, apache.pw_gid)
			os.chown(self.authz_file, apache.pw_uid, apache.pw_gid)
			os.chown(self.userprop_file, apache.pw_uid, apache.pw_gid)
			os.chown(self.access_file, apache.pw_uid, apache.pw_gid)
		except OSError:
			print '''
 *** Failed to change permissions to apache user, are you root?
'''

		# create apache.conf
		self.create_apache_conf(submin_conf_file)

		print 'created submin configuration with default user admin (password: admin)'

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


