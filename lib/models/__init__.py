from bootstrap import fimport, settings

def getBackend(model):
	"""Gets the backend-module for a certain model."""

	return fimport("plugins.backends.%s.%s" % (settings.backend, model),
			       "plugins.backends.%s" % settings.backend)

def backendSetup():
	"""Calls setup, this is usually only done when initialising the environment
	or a new backend is used."""

	# Calls plugins.backends.<backend>.setup()
	fimport("plugins.backends.%s" % settings.backend,
			"plugins.backends").setup()

def backendInit(pass_settings=settings):
	"""Initialises the backend: either opens a database connection or does
	other initialisation."""

	fimport("plugins.backends.%s" % pass_settings.backend,
			"plugins.backends").init(pass_settings)

def backendTearDown():
	"""Teardown is sometimes needed to close databases, etc."""

	fimport("plugins.backends.%s" % settings.backend,
			"plugins.backends").teardown()
