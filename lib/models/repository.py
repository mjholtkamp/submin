from config.config import Config

class Repository(object):
	class DoesNotExist(Exception):
		pass

	def __init__(self, name):
		config = Config()

		self.name = name
		self.config = config

#		if self.name not in config.authz.groups():
#			raise Repository.DoesNotExist

		self.authz_paths = self.config.authz.paths(self.name)
		self.authz_paths.sort()
		self.dirs = self.getsubdirs("")

	def getsubdirs(self, path):
		import pysvn
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
				dirs.append(name[name.rindex('/') + 1:])

		return dirs

	def __str__(self):
		return self.name
