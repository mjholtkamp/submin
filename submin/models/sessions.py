import os
from submin.models import storage as models_storage
from submin.models.exceptions import UnknownKeyError

storage = models_storage.get("sessions")

def get(key, default=None):
	"""Return value for option *key*. If the key does not exist and *default*
	   is None, raises UnknownKeyError. If the key does not exist and *default*
	   is not None, it will return *default*"""
	try:
		val, expires = storage.get(key)
	except UnknownKeyError:
		if default == None:
			raise # just pass on the exception

		val = default

	return (val, expires)

def set(key, value, expires):
	storage.set(key, value, expires)

def unset(key):
	storage.unset(key)

__doc__ = """
Storage contract
================

Options consists of a key and a value pair

* get(key)
	Returns a tuple of (value, expires) corresponding to *key*. The expiry
	is a unix timestamp. Raises UnknownKeyError if it doesn't exist.

* set(key, value, expires)
	Sets session *key* to *value* with expiry *expires* (unix timestamp).

* unset(key)
	removes *key* and data associated with it from storage.
"""
