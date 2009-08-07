from __init__ import db, execute

_options = {}

def value(key):
	return _options[key]

def set_value(key, value):
	_options[key] = value

def options():
	return _options
