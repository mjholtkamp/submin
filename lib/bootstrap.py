import os, sys

def fimport(filename, fromlist=[]):
	return __import__(filename, globals(), locals(), fromlist)


class Settings(object):
	"""Loads the settings file lazily.
	
	This means that on the first time a setting is requested, the settings are
	read."""
	def __init__(self):
		self.__dict__['settings'] = None

	def load(self):
		if not os.environ.has_key('SUBMIN_ENV'):
			raise Exception('Settings cannot be imported, please set the SUBMIN_ENV' +\
			' environment variable to the submin base directory')

		sys.path.insert(0, os.path.join(os.environ['SUBMIN_ENV'], 'conf'))

		self.__dict__['settings'] = fimport('settings')

		del sys.path[0]

	def __getattr__(self, attr):
		if not self.__dict__['settings']:
			self.load()
		return getattr(self.__dict__['settings'], attr)

	def __setattr__(self, attr, value):
		if not self.__dict__['settings']:
			self.load()
		return setattr(self.__dict__['settings'], attr, value)

settings = Settings()

def setSettings(new_settings):
	global settings
	settings = new_settings
