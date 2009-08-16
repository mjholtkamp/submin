from bootstrap import fimport, settings, SettingsException

class BackendException(Exception):
	pass

def get(model):
	"""Gets the backend-module for a certain model."""
	try:
		backend = fimport("plugins.backends.%s.%s" % (settings.backend, model),
			       "plugins.backends.%s" % settings.backend)
	except SettingsException, e:
		raise BackendException(str(e))

	return backend

def setup():
	"""Calls setup, this is usually only done when initialising the environment
	or a new backend is used."""

	# Calls plugins.backends.<backend>.setup()
	try:
		fimport("plugins.backends.%s" % settings.backend,
				"plugins.backends").setup()
	except SettingsException, e:
		raise BackendException(str(e))

def open(pass_settings=settings):
	"""opens the backend: either opens a database connection or does
	other initialisation."""
	try:
		fimport("plugins.backends.%s" % pass_settings.backend,
				"plugins.backends").init(pass_settings)
	except SettingsException, e:
		raise BackendException(str(e))

def close():
	"""close() will close databases, if approriate."""
	try:
		fimport("plugins.backends.%s" % settings.backend,
				"plugins.backends").teardown()
	except SettingsException, e:
		raise BackendException(str(e))
