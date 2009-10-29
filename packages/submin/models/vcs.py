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

def export_auth_user():
	"""Export vcs-specific authorization/authentication information.
	For example, regenerate authz file for subversion HTTP access."""
	for vcstype in list():
		export_auth(vcstype, "user")

def export_auth_group():
	"""Export vcs-specific authorization/authentication information.
	For example, regenerate authz file for subversion HTTP access."""
	for vcstype in list():
		export_auth(vcstype, "group")

def export_auth_repository(vcstype):
	"""Export vcs-specific authorization/authentication information.
	For example, regenerate authz file for subversion HTTP access."""
	export_auth(vcstype, "repository")
	
def export_auth(vcstype, authtype):
	try:
		backend = fimport("plugins.vcs.%s.%s" % (vcstype, "export"),
			       "plugins.vcs.%s" % vcstype)
	except ImportError, e:
		raise VCSException(e)

	backend.export_auth(authtype)
