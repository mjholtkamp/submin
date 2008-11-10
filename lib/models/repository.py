from config.config import Config
import exceptions

class Repository(object):
	class DoesNotExist(Exception):
		pass

	def __init__(self, name):
		config = Config()

		self.name = name
		self.config = config
		self.signature = "### SUBMIN AUTOCONFIG, DO NOT ALTER FOLLOWING LINE ###\n"

		self.authz_paths = self.config.authz.paths(self.name)
		self.authz_paths.sort()
		self.dirs = self.getsubdirs("")

	def getsubdirs(self, path):
		'''Return subdirs (not recursive) of 'path' relative to our reposdir
		Subdirs are returned as a hash with two entities: 'name' and 
		'has_subdirs', which should be self-explanatory.'''
		try:
			import pysvn
		except exceptions.ImportError, e:
			raise Exception('Module pysvn not found, please install it')
		import os

		client = pysvn.Client()
		reposdir = self.config.get('svn', 'repositories')
		url = 'file://' + reposdir
		url = os.path.join(url, self.name)
		url = os.path.join(url, path)

		files = client.ls(url, recurse=False)
		dirs = []
		for file in files:
			if file['kind'] == pysvn.node_kind.dir:
				name = file['name']
				entry = {}
				entry['name'] = name[name.rindex('/') + 1:]
				entry['has_subdirs'] = self.hassubdirs(os.path.join(url, entry['name']))
				dirs.append(entry)

		return dirs

	def hassubdirs(self, url):
		import pysvn
		import os

		client = pysvn.Client()
		files = client.ls(url, recurse=False)
		for file in files:
			if str(file['kind']) == 'dir':
				return True

		return False
	
	def notificationsEnabled(self):
		import os

		reposdir = self.config.get('svn', 'repositories')
		hook = os.path.join(reposdir, self.name, 'hooks', 'post-commit')
		try:
			f = open(hook, 'r')
		except IOError:
			return False # assume it does not exist
		
		# if we find the signature, assume it is installed
		if self.signature in f.readlines():
			return True
		return False

	def changeNotifications(self, enable=True):
		"""Add or remove our script to/from the post-commit hook"""
		import os
		config = Config()

		line_altered = False
		reposdir = self.config.get('svn', 'repositories')
		hook = os.path.join(reposdir, self.name, 'hooks', 'post-commit')
		bindir = self.config.get('backend', 'bindir')
		fullpath = os.path.join(bindir, 'post-commit.py')
		config_file = os.environ['SUBMIN_CONF']
		new_hook = '/usr/bin/python %s "%s" "$1" "$2"\n' % (fullpath, config_file)
		f = open(hook, 'a+')
		f.seek(0, 2) # seek to end of file, not all systems do this

		if f.tell() != 0:
			f.seek(0)
			alter_line = False
			new_file_content = []
			for line in f.readlines():
				if alter_line:
					if enable:
						new_file_content.append(new_hook)
					alter_line = False
					line_altered = True
					continue # filter out command

				if line == self.signature:
					alter_line = True
					if not enable:
						continue # filter out signature

				new_file_content.append(line)
		
			f.truncate(0)
			f.writelines(new_file_content)
		else:
			if enable:
				f.write("#!/bin/sh\n")

		if not line_altered and enable:
			f.write(self.signature)
			f.write(new_hook)
		f.close()
		os.chmod(hook, 0755)

	def __str__(self):
		return self.name
