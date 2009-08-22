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

	def env_path(self, key=None):
		base = Path(os.environ['SUBMIN_ENV'])
		if key == None:
			return base

		val = self.value(key)
		if val == None:
			raise Exception("no such key")

		path = Path(val)
		if path.absolute:
			return path
		
		return base + path

	def static_path(self, subdir):
		# __file__ returns <submin-static-dir>/lib/models/options.py
		base_lib = os.path.dirname(os.path.dirname(__file__))
		base = Path(os.path.dirname(base_lib))
		
		return base + subdir

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
