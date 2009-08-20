from bootstrap import fimport

class VCSException(Exception):
	pass

def list():
	return ['svn']

def get(vcstype, model):
	"""Gets the vcs-backend for a certain type and model."""
	try:
		backend = fimport("plugins.vcs.%s.%s" % (vcstype, model),
			       "plugins.vcs.%s" % vcstype)
	except ImportError, e:
		raise VCSException(e)

	return backend
