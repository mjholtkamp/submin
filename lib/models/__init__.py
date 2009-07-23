from bootstrap import fimport, settings

def getBackend(model):
	return fimport("plugins.backends.%s.%s" % (settings.backend, model),
			       "plugins.backends.%s" % settings.backend)

def backendSetup():
	# Calls plugins.backends.<backend>.setup()
	fimport("plugins.backends.%s" % settings.backend,
			"plugins.backends").setup()
