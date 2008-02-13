import os.path

class Path(object):
	def __init__(self, path, append_slash=False, absolute=True):
		self.append_slash = append_slash
		self.absolute = absolute
		self.path = self.canonicalize(path)

	def basename(self):
		return os.path.basename(self.path)

	def dirname(self):
		return os.path.dirname(self.path)

	def join(self, other):
		if isinstance(other, Path):
			other = other.path.lstrip('/')

		other = os.path.join(self.path, other)

		return self.canonicalize(other)

	def canonicalize(self, path):
		'''Return canonical form of path, depending on options'''
		if not self.absolute:
			path = path.lstrip('/')
		else:
			if path[0] != '/':
				path = '/' + path

		if self.append_slash:
			return path + '/'

		return path.rstrip('/')

	def __add__(self, other):
		return self.join(other)

	def __str__(self):
		return self.path

