from submin.bootstrap import fimport, settings, SettingsException, setSettings
from submin.models.exceptions import StorageAlreadySetup, StorageError

def get(model):
	"""Gets the storage-module for a certain model."""
	try:
		storage = fimport("submin.plugins.storage.%s.%s" % (settings.storage, model),
			       "submin.plugins.storage.%s" % settings.storage)
	except SettingsException, e:
		raise StorageError(str(e))

	return storage

def database_evolve(*args, **kwargs):
	"""Calls database_evolve, this is usually only done when initialising the
	environment or a new storage is used, or if the code suggests there is a
	new version of the database, which is not reflected in the production
	database yet."""
	# Calls plugins.storage.<storage>.database_evolve()
	try:
		fimport("submin.plugins.storage.%s" % settings.storage,
				"submin.plugins.storage").database_evolve(*args, **kwargs)
	except SettingsException, e:
		raise StorageError(str(e))

def open(pass_settings=None):
	"""opens the storage: either opens a database connection or does
	other initialisation."""
	if pass_settings:
		setSettings(pass_settings)

	try:
		fimport("submin.plugins.storage.%s" % settings.storage,
				"submin.plugins.storage").open(settings)
	except SettingsException, e:
		raise StorageError(str(e))

def close():
	"""close() will close databases, if approriate."""
	try:
		fimport("submin.plugins.storage.%s" % settings.storage,
				"submin.plugins.storage").close()
	except SettingsException, e:
		raise StorageError(str(e))
