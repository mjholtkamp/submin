import os
from submin import models
from submin.path.path import Path
from submin.models.exceptions import UnknownKeyError

backend = models.backend.get("options")

class Options(object):
	def value(self, key):
		return backend.value(key)

	def set_value(self, key, value):
		backend.set_value(key, value)

	def options(self):
		return backend.options()

	def url_path(self, key):
		return Path(self.value(key), append_slash=True)

	def env_path(self, key=None):
		from submin.bootstrap import settings # for base_dir
		base = Path(settings.base_dir)
		if key == None:
			return base

		path = Path(self.value(key))
		if path.absolute:
			return path

		return base + path

	def static_path(self, subdir):
		# __file__ returns <submin-static-dir>/lib/models/options.py
		base_lib = os.path.dirname(__file__)
		base = Path(os.path.dirname(base_lib)) + 'static'

		return base + subdir

__doc__ = """
Backend contract
================

Options consists of a key and a value pair

* value(key)
	Returns the value of *key*. Raises UnknownKeyError if it doesn't exist.

* set_value(key, value)
	Sets option *key* to *value*

* options()
	Returns a dict of all keys and values.
"""
