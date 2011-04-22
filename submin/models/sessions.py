import os
from submin.models import storage as models_storage
from submin.models.exceptions import UnknownKeyError

storage = models_storage.get("sessions")

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

__doc__ = """
Storage contract
================

Options consists of a key and a value pair

* value(key)
	Returns the value of *key*. Raises UnknownKeyError if it doesn't exist.

* set_value(key, value)
	Sets session *key* to *value*
"""
