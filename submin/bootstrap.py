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
		if 'SUBMIN_ENV' not in os.environ:
			raise SettingsException('Settings cannot be imported, please ' +
				'set the SUBMIN_ENV environment variable to the submin base ' +
				'directory')

		base_dir = os.environ['SUBMIN_ENV']
		sys.path.insert(0, os.path.join(base_dir, 'conf'))

		try:
			self.setSettings(fimport('settings'))
		except ImportError as e:
			raise SettingsException('Could not load settings: file does not ' +
				'exist or insufficient permissions')

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

class SubminInstallationCheck(object):
	def __init__(self, submin_dir, environ=None):
		self.submin_dir = submin_dir
		self.new_env = None
		self.old_env = None

		self.environ = os.environ
		if environ:
			self.environ = environ

		self.check_env()
		self.ok = self.new_env and not self.old_env
	
	def check_env(self):
		if 'SUBMIN_ENV' in self.environ:
			self.new_env = self.environ['SUBMIN_ENV']
		if 'SUBMIN_CONF' in self.environ:
			self.old_env = self.environ['SUBMIN_CONF']

	def error_page(self):
		from template.template import Template
		import template.template_commands
		fname = os.path.join(self.submin_dir, 'static', 'templates', 'error_config.html')
		fp = file(fname, 'r')
		variables = {
			'new_env': self.new_env,
			'old_env': self.old_env,
		}
		tpl = Template(fp, variables)
		return tpl.evaluate()
