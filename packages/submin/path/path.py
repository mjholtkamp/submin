import os.path

class Path(object):
	def __init__(self, path, append_slash=False, absolute=None):
		self.append_slash = append_slash
		self.absolute = absolute
		self.path = self.canonicalize(path)

	def basename(self):
		return os.path.basename(self.path)

	def dirname(self):
		return os.path.dirname(self.path)

	def copy(self, path=None):
		if path is None:
			path = self.path

		p = Path(path, append_slash=self.append_slash, absolute=self.absolute)
		return p

	def join(self, other):
		if isinstance(other, Path):
			other = other.path.lstrip('/')
		else:
			other = other.lstrip('/')

		joined = os.path.join(self.path, other)
		path = self.canonicalize(joined)

		return self.copy(path)

	def canonicalize(self, path):
		'''Return canonical form of path, depending on options'''
		# autodetect absolute/relative paths
		if self.absolute == None:
			if len(path) > 0 and path[0] == '/':
				self.absolute = True
			else:
				self.absolute = False

		path = path.rstrip('/')

		if not self.absolute:
			path = path.lstrip('/')
		else:
			if path == '' or path[0] != '/':
				path = '/' + path

		if self.append_slash and path != '/':
			return path + '/'

		return path

	def __add__(self, other):
		return self.join(other)

	def __str__(self):
		return self.path

