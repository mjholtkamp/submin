import os
import models
from path.path import Path
backend = models.backend.get("options")

class Options(object):
	def value(self, key):
		return backend.value(key)

	def set_value(self, key, value):
		backend.set_value(key, value)

	def options(self):
		return backend.options()

	def path(self, key):
		path = Path(self.value(key))
		if path.absolute:
			return path
		
		return Path(self.base_path()) + path

	def base_path(self):
		return os.environ['SUBMIN_ENV']

__doc__ = """
Backend contract
================

Options consists of a key and a value pair

* value(key)
	Returns the value of *key*

* set_value(key, value)
	Sets option *key* to *value*

* options()
	Returns a dict of all keys and values
"""
