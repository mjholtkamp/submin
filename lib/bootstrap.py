import os, sys

def fimport(filename, fromlist=[]):
	return __import__(filename, globals(), locals(), fromlist)

class SettingsException(Exception):
	pass

class Settings(object):
	"""Loads the settings file lazily.
	
	This means that on the first time a setting is requested, the settings are
	read."""
	def __init__(self):
		# use __dict__ to avoid loading the settings file
		self.__dict__['settings'] = None

	def load(self):
		if not os.environ.has_key('SUBMIN_ENV'):
			raise SettingsException('Settings cannot be imported, please set the SUBMIN_ENV' +\
			' environment variable to the submin base directory')

		base_dir = os.environ['SUBMIN_ENV']
		sys.path.insert(0, os.path.join(base_dir, 'conf'))

		self.setSettings(fimport('settings'))

		del sys.path[0]
		# we can now set directly because __setattr__ will not call load
		self.base_dir = base_dir

	def __getattr__(self, attr):
		if not self.__dict__['settings']:
			self.load()
		return getattr(self.__dict__['settings'], attr)

	def __setattr__(self, attr, value):
		if not self.__dict__['settings']:
			self.load()
		return setattr(self.__dict__['settings'], attr, value)

	def setSettings(self, settings):
		self.__dict__['settings'] = settings

settings = Settings()

def setSettings(new_settings):
	settings.setSettings(new_settings)
