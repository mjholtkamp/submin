import os
from submin.models import storage as models_storage
from submin.path.path import Path
from submin.models.exceptions import UnknownKeyError

storage = models_storage.get("options")

def value(key, default=None):
	"""Return value for option *key*. If the key does not exist and *default*
	   is None, raises UnknownKeyError. If the key does not exist and *default*
	   is not None, it will return *default*"""
	try:
		val = storage.value(key)
	except UnknownKeyError:
		if default == None:
			raise # just pass on the exception

		val = default

	return val

def set_value(key, value):
	storage.set_value(key, value)

def unset_value(key):
	storage.unset_value(key)

def options():
	return storage.options()

def url_path(key):
	return Path(value(key), append_slash=True)

def env_path(key=None):
	from submin.bootstrap import settings # for base_dir
	base = Path(os.path.normpath(settings.base_dir))
	if key == None:
		return base

	path = Path(value(key))
	if path.absolute:
		return path

	return base + path

def static_path(subdir):
	# __file__ returns <submin-static-dir>/lib/models/options.py
	base_lib = os.path.dirname(__file__)
	base = Path(os.path.dirname(base_lib)) + 'static'

	return base + subdir

__doc__ = """
Storage contract
================

Options consists of a key and a value pair

* value(key)
	Returns the value of *key*. Raises UnknownKeyError if it doesn't exist.

* set_value(key, value)
	Sets option *key* to *value*

* options()
	Returns a dict of all keys and values.
"""
