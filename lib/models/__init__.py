from bootstrap import fimport, settings

def getBackend(model):
	return fimport("plugins.backends.%s.%s" % (settings.backend, model),
			       "plugins.backends.%s" % settings.backend)
