import os.path

class Path(object):
	def __init__(self, path, append_slash=False):
		self.path = path
		self.append_slash = append_slash

	def basename(self):
		return os.path.basename(self.path)

	def dirname(self):
		return os.path.dirname(self.path)

	def join(self, other):
		if isinstance(other, Path):
			other = other.path

		if other[0] == "/":
			other = other.lstrip('/')

		newpath = os.path.join(self.path, other)
		if self.append_slash:
			newpath += "/"
		else:
			newpath = newpath.rstrip("/")
		return newpath

	def __add__(self, other):
		return self.join(other)

	def __str__(self):
		path = self.path
		if self.append_slash:
			path += "/"
		else:
			path = path.rstrip("/")
		return path
