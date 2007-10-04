#!/usr/bin/python
import re
import sys

class Installer:
	def __init__(self):
		self.paths = dict(svn='/var/lib/svn/', \
			htpasswd='/etc/apache2/svn/htpasswd', \
			svn_authz='/etc/apache2/svn/authz', \
			config='/etc/submerge/submerge.conf')

		self.yes = re.compile('([yY]([eE][sS])?|)$')

	def install(self):
		while not self.ask_paths_ok():
			self.ask_config()

		self.write_config()
		self.ask_users()
		self.ask_apache()

	def ask_paths_ok(self):
		yes = raw_input('''Installing with:

        svn dir : %(svn)s
  htpasswd file : %(htpasswd)s
 svn authz file : %(svn_authz)s
    config file : %(config)s

Are these settings ok? [Y/n]: ''' % self.paths)

		if self.yes.match(yes):
			return True

		return False

	def ask_apache(self):
		#vhost = raw_input('Install for virtual host? [Y/n] ')
		#if self.yes.match(vhost):
		#	self.apache_vhost()
		#	return

		subdir = raw_input('Install for subdir? [Y/n] ')
		if self.yes.match(subdir):
			self.apache_subdir()
			return

		print "Not configuring apache"

	def apache_vhost(self):
#cp /usr/share/submerge/apache.conf.virtual-host-example /etc/apache2/sites-available/submerge
		print "vhost not yet implemented, sorry"

	def apache_subdir(self):
		import os
		configname = os.path.basename(self.paths['config'])
		configname = configname.replace('.conf', '')
		if configname != 'submerge':
			configname = '-' + configname
		else:
			configname = ''

		src = '/usr/share/submerge/examples/apache.conf.subdir'
		dst = '/etc/submerge/apache' + configname + '.conf'
		if not os.path.exists(os.path.dirname(dst)):
			os.makedirs(os.path.dirname(dst))

		if os.path.exists(dst):
			os.rename(dst, dst + '.submerge-old')

		f = file(dst, 'w')
		for line in file(src).readlines():
			line = line.replace('/etc/submerge/submerge.conf', \
				self.paths['config'])

			f.write(line)

		src = dst
		dst = '/etc/apache2/conf.d/submerge' + configname + '.conf'
		if not os.path.exists(dst):
			os.symlink(src, dst)

		os.system('apache2ctl configtest && apache2ctl restart')

	def ask_config(self):
		self.ask_svn_path()
		self.ask_config_path()
		self.ask_svn_authz_path()
		self.ask_htpasswd_path()

	def ask_htpasswd_path(self):
		import os
		sure = False
		while not sure:
			path = raw_input(\
				'Which htpasswd file should be used? [%s]' % \
				self.paths['htpasswd'])

			if path == '':
				path = self.paths['htpasswd']

			if not os.path.exists(path):
				yes = raw_input("Are you sure? %s doesn't exist [Y/n] " % path)
				if self.yes.match(yes):
					sure = True
					self.clean_install = True
			else:
				sure = True

		self.paths['htpasswd'] = path

	def ask_svn_path(self):
		import os
		svn_path = raw_input('Where are svn repositories found? [%s] ' % \
			self.paths['svn'])

		if svn_path == '':
			svn_path = self.paths['svn']

		self.paths['svn'] = svn_path

	def ask_config_path(self):
		import os
		sure = False

		while not sure:
			config_path = raw_input('Where should the config be placed? [%s] '\
				% self.paths['config'])

			if config_path == '':
				config_path = self.paths['config']

			if os.path.exists(config_path):
				yes = raw_input('Path already exists, overwrite? [Y/n]')
				if self.yes.match(yes):
					sure = True
			else:
				sure = True

		self.paths['config'] = config_path

	def ask_svn_authz_path(self):
		path = raw_input('''
Submerge uses an authz file to store users/groups, like svn does. For maximum
ease-of-use, use the same authz-file for svn/submerge (and maybe trac!)

Which svn authz should Submerge use? [%s] ''' % self.paths['svn_authz'])

		if path == '':
			return

		self.paths['svn_authz'] = path

	def make_paths(self):
		import os
		for path in self.paths.itervalues():
			if not os.path.exists(os.path.dirname(path)):
				os.makedirs(os.path.dirname(path))

		print "make sure %s has write permissions for the webserver" % \
			self.paths['svn']

	def write_config(self):
		import ConfigParser

		self.make_paths()

		cp = ConfigParser.ConfigParser()
		cp.add_section('svn')
		config = dict(authz_file=self.paths['svn_authz'], \
			access_file=self.paths['htpasswd'], \
			repositories=self.paths['svn'])

		for (option, value) in config.iteritems():
			cp.set('svn', option, value)

		f = open(self.paths['config'], 'w+')
		cp.write(f)
		f.close()

	def ask_users(self):
		"""Ask about users, so the system has at least one admin user"""
		from authz import Authz, UnknownGroupError
		from htpasswd import HTPasswd
		import os

		authz = Authz(self.paths['svn_authz'])
		members = []
		try:
			members = authz.members('submerge-admins')
		except UnknownGroupError:
			authz.addGroup('submerge-admins')
			pass

		user = ''
		if len(members) == 0:
			while user == '':
				user = raw_input('Enter a username to act as submerge admin: ')

			authz.addMember('submerge-admins', user)
			print 'user %s added' % user

		"""Now add password for user, if it didn't have one already"""
		htp = HTPasswd(self.paths['htpasswd'])
		if not htp.exists(user):
			passwd = ''
			passwd_check = '';
			while passwd == '' or passwd != passwd_check:
				from getpass import getpass
				passwd = ''
				passwd_check = '';
				passwd = getpass('Password for user %s: ' % user)
				passwd_check = getpass('Confirm password: ')

			htp.add(user, passwd)
			htp.flush()

		self.fix_permissions()

	def fix_permissions(self):
		import pwd
		import os
		user = 'www-data'
		for line in file('/etc/apache2/apache2.conf'):
			if 'User ' in line:
				user = line.replace('User ', '').strip('\n')

		pwent = pwd.getpwnam(user)
		os.chown(self.paths['svn_authz'], pwent.pw_uid, pwent.pw_gid)
		os.chown(self.paths['htpasswd'], pwent.pw_uid, pwent.pw_gid)

if __name__ == '__main__':
	sys.path.append('/usr/share/submerge/www/lib')
	try:
		installer = Installer()
		installer.install()
	except KeyboardInterrupt:
		print
