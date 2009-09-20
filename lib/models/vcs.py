from bootstrap import fimport

class VCSException(Exception):
	pass

def list():
	import pkgutil, os
	# __file__ returns <submin-dir>/lib/models/vcs.py
	libdir = os.path.dirname(os.path.dirname(__file__))
	vcsdir = os.path.join(libdir, 'plugins', 'vcs')
	return [name for _, name, _ in pkgutil.iter_modules([vcsdir])]

def get(vcstype, model):
	"""Gets the vcs-backend for a certain type and model."""
	try:
		backend = fimport("plugins.vcs.%s.%s" % (vcstype, model),
			       "plugins.vcs.%s" % vcstype)
	except ImportError, e:
		raise VCSException(e)

	return backend
