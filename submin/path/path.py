import os.path

try:
	superclass = unicode
except NameError:
	# Must be Python 3.x
	superclass = str

def _canonicalize(path, append_slash, absolute):
	'''Return canonical form of path, depending on options'''
	# autodetect absolute/relative paths
	if absolute == None:
		if len(path) > 0 and path[0] == '/':
			absolute = True
		else:
			absolute = False

	path = path.rstrip('/')

	if not absolute:
		path = path.lstrip('/')
	else:
		if path == '' or path[0] != '/':
			path = '/' + path

	if append_slash and path != '/':
		return (path + '/', absolute)

	return (path, absolute)

class Path(superclass):
	def __new__(cls, path, append_slash=False, absolute=None):
		(path, absolute) = _canonicalize(path, append_slash, absolute)
		self = super(Path, cls).__new__(cls, path)
		self.append_slash = append_slash
		self.absolute = absolute
		return self

	def exists(self):
		return os.path.exists(self)

	def basename(self):
		return os.path.basename(self)

	def dirname(self):
		return os.path.dirname(self)

	def copy(self):
		return Path(superclass(self), append_slash=self.append_slash, absolute=self.absolute)

	def join(self, other):
		other = other.lstrip('/')
		joined = os.path.join(superclass(self), other)
		return Path(joined, append_slash=self.append_slash, absolute=self.absolute)

	def __add__(self, other):
		return self.join(other)
