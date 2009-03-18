# -*- coding: utf-8 -*-
from config.config import Config
from path.path import Path
import commands
import exceptions

def listRepositories(session_user, only_invalid=False):
	config = Config()
	repositories = []
	if session_user.is_admin:
		repository_names = repositoriesOnDisk()
		repository_names.sort()

		for repos in repository_names:
			try:
				r = Repository(repos)
				if not only_invalid:
					repositories.append(repos)
			except Repository.DoesNotExist:
				if only_invalid:
					repositories.append(repos)

	return repositories

def repositoriesOnDisk():
	"""Returns all repositories that are found on disk"""
	import glob, os.path
	config = Config()
	reposdir = config.getpath('svn', 'repositories')
	reps = glob.glob(str(reposdir + '*'))
	repositories = []
	for rep in reps:
		if os.path.isdir(rep):
			repositories.append(rep[rep.rfind('/') + 1:])

	repositories.sort()

	return repositories

class Repository(object):
	"""Internally, this class uses unicode to represent files and directories.
It is converted to UTF-8 (or other?) somewhere in the dispatcher."""

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
		import os

		reposdir = str(self.config.getpath('svn', 'repositories'))
		url = 'file://' + os.path.join(reposdir, self.name, path)

		files = self.get_entries(url)
		dirs = []
		for f in files:
			if f['kind'] == 'dir':
				hassubdirs = self.hassubdirs(os.path.join(url, f['name']))
				entry = {}
				entry['name'] = f['name']
				entry['has_subdirs'] = hassubdirs
				dirs.append(entry)

		return dirs

	def get_entries(self, url):
		import commands
		# convert from unicode, because we are going to use it 'outside'
		url = url.encode('utf-8')
		# Escape single quotes to prevent injection
		url = url.replace("'", "\\'")
		(code, text) = commands.getstatusoutput("LC_CTYPE=UTF-8 svn ls '%s'" % url)
		if code != 0:
			raise self.DoesNotExist()

		text = text.split('\n')

		entries = []
		for entry in text:
			if len(entry) < 1:
				continue

			e = {}
			# Assume entries are utf-8
			name = unicode(entry, 'utf-8')
			if entry[-1] == '/':
				e['kind'] = 'dir'
				e['name'] = name[:-1]
			else:
				e['kind'] = 'file'
				e['name'] = name
			entries.append(e)

		return entries

	def hassubdirs(self, url):
		import os

		files = self.get_entries(url)
		for f in files:
			if f['kind'] == 'dir':
				return True # only one is enough

		return False

	def notificationsEnabled(self):
		import os

		reposdir = self.config.getpath('svn', 'repositories')
		hook = reposdir + self.name + 'hooks' + 'post-commit'
		try:
			f = open(str(hook), 'r')
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
		reposdir = self.config.getpath('svn', 'repositories')
		hook = reposdir + self.name + 'hooks' + 'post-commit'
		bindir = self.config.getpath('backend', 'bindir')
		fullpath = bindir + 'post-commit.py'
		# XXX ugly code :(
		if config.version == 1:
			config_file = os.environ['SUBMIN_CONF']
		else:
			config_file = os.environ['SUBMIN_ENV']

		new_hook = '/usr/bin/python %s "%s" "$1" "$2"\n' % \
				(str(fullpath), config_file)

		f = open(str(hook), 'a+')
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
		os.chmod(str(hook), 0755)

	def remove(self):
		config = Config()
		reposdir = config.getpath('svn', 'repositories')
		newrepos = reposdir + self.name
		if not newrepos.absolute:
			raise Exception("Error, repository path is relative, this should be fixed")

		cmd = 'rm -rf "%s"' % newrepos
		(exitstatus, outtext) = commands.getstatusoutput(cmd)
		if exitstatus == 0:
			return
		raise Exception("could not remove repository %s" % self.name)

	def __str__(self):
		return self.name
