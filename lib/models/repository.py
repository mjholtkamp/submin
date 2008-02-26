from config.config import Config

class Repository(object):
	class DoesNotExist(Exception):
		pass

	def __init__(self, name):
		config = Config()

		self.name = name
		self.config = config

		self.authz_paths = self.config.authz.paths(self.name)
		self.authz_paths.sort()
		self.dirs = self.getsubdirs("")

	def getsubdirs(self, path):
		'''Return subdirs (not recursive) of 'path' relative to our reposdir
		Subdirs are returned as a hash with two entities: 'name' and 
		'has_subdirs', which should be self-explanatory.'''
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
			if file['kind'] == 'dir':
				return True

		return False


	def __str__(self):
		return self.name
