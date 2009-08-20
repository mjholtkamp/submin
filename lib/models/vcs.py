from bootstrap import fimport

class VCSException(Exception):
	pass

def list():
	import pkgutil
	return [name for _, name, _ in pkgutil.iter_modules(['plugins/vcs'])]

def get(vcstype, model):
	"""Gets the vcs-backend for a certain type and model."""
	try:
		backend = fimport("plugins.vcs.%s.%s" % (vcstype, model),
			       "plugins.vcs.%s" % vcstype)
	except ImportError, e:
		raise VCSException(e)

	return backend
