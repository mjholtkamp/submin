#!/usr/bin/python
import re

#mkdir -p /var/log/apache2/submerge /usr/share/submerge /etc/submerge
#cp -a www/* /usr/share/submerge
#find /usr/share/submerge/ -name .svn -exec rm -rf \{} \;
#cp -i submerge.example.conf /etc/submerge/submerge.conf
class Installer:
	def __init__(self):
		self.htpasswd_path = '/usr/share/submerge/.htpasswd'
		self.svn_dir = '/var/lib/svn'
		self.config_path = '/etc/submerge/submerge.conf'
		self.svn_authz_path = '/etc/apache2/svn.authz'
		self.yes = re.compile('([yY]([eE][sS])?|)$')
		self.clean_install = False

	def install(self):
		self.ask_apache()
		self.ask_config()

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
		self.ask_svn_dir()
		self.ask_config_path()
		self.ask_svn_authz_path()
		self.ask_htpasswd_path()
		self.write_config()

	def ask_htpasswd_path(self):
		import os
		sure = False
		while not sure:
			path = raw_input(\
				'Which htpasswd file should be used? [%s]' % \
				self.htpasswd_path)

			if path == '':
				path = self.htpasswd_path

			if not os.path.exists(path):
				yes = raw_input("Are you sure? %s doesn't exist [Y/n] " % path)
				if self.yes.match(yes):
					sure = True
					self.clean_install = True
			else:
				sure = True

		self.htpasswd_path = path

	def ask_svn_dir(self):
		import os
		svn_dir = raw_input('Where are svn repositories found? [%s] ' % \
			self.svn_dir)

		if svn_dir == '':
			svn_dir = self.svn_dir

		# if user doesn't have this dir, probably means clean install
		if not os.path.exists(svn_dir):
			os.mkdir(svn_dir)
			self.clean_install = True

		self.svn_dir = svn_dir

	def ask_config_path(self):
		import os
		sure = False

		while not sure:
			config_path = raw_input('Where should the config be placed? [%s] '\
				% self.config_path)

			if config_path == '':
				config_path = self.config_path

			if os.path.exists(config_path):
				yes = raw_input('Path already exists, overwrite? [Y/n]')
				if self.yes.match(yes):
					sure = True
			else:
				# make sure path exists
				os.mkdir(os.path.dirname(config_path))
				sure = True

	def ask_svn_authz_path(self):
		path = raw_input('''
Submerge uses an authz file to store users/groups, like svn does. For maximum
ease-of-use, use the same authz-file for svn/submerge (and maybe trac!)

Which svn authz should Submerge use? [%s] ''' % self.svn_authz_path)

		if path == '':
			return

		self.svn_authz_path = path

	def write_config(self):
		import ConfigParser

		cp = ConfigParser.ConfigParser()
		cp.add_section('svn')
		config = dict(authz_file=self.svn_authz_path, \
			access_file=self.htpasswd_path, \
			repositories=self.svn_dir)

		for (option, value) in config.iteritems():
			cp.set('svn', option, value)

		f = open(self.config_path, 'w+')
		cp.write(f)
		f.close()


if __name__ == '__main__':
	installer = Installer()
	installer.install()
