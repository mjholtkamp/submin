#!/usr/bin/python
import re
import sys

#mkdir -p /var/log/apache2/submerge /usr/share/submerge /etc/submerge
#cp -a www/* /usr/share/submerge
#find /usr/share/submerge/ -name .svn -exec rm -rf \{} \;

class Installer:
	def __init__(self):
		self.paths = dict(svn='/var/lib/svn/', \
			htpasswd='/etc/apache2/svn/htpasswd', \
			svn_authz='/etc/apache2/svn/authz', \
			config='/etc/submerge/submerge.conf')

		self.yes = re.compile('([yY]([eE][sS])?|)$')

	def install(self):
		while not self.ask_paths_ok():
			self.ask_apache()
			self.ask_config()

		self.write_config()
		self.ask_users()

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
		vhost = raw_input('Install for virtual host? [Y/n] ')
		if self.yes.match(vhost):
			self.apache_vhost()
			return

		subdir = raw_input('Install for subdir? [Y/n] ')
		if self.yes.match(subdir):
			self.apache_subdir()
			return

		print "Not configuring apache"

	def apache_vhost(self):
#cp /usr/share/submerge/apache.conf.virtual-host-example /etc/apache2/sites-available/submerge
		print "vhost not yet implemented, sorry"
		pass

	def apache_subdir(self):
#cp /usr/share/submerge/.htaccess.example /usr/share/submerge/.htaccess
		print "subdir not yet implemented, sorry"
		pass

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

		print "make sure %s permissions allow the webserver write" % \
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
				passwd = ''
				passwd_check = '';
				passwd = raw_input('Password for user %s: ' % user)
				passwd_check = raw_input('Confirm password: ')

			htp.add(user, passwd)
			htp.flush()

if __name__ == '__main__':
	sys.path.append('/usr/share/submerge/www/lib')
	try:
		installer = Installer()
		installer.install()
	except KeyboardInterrupt:
		print
