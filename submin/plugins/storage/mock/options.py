from submin.models.exceptions import UnknownKeyError

_options = {}

def clear_options():
	_options.clear()

def value(key):
	try:
		return _options[key]
	except KeyError:
		raise UnknownKeyError

def set_value(key, value):
	_options[key] = value

def options():
	return _options
