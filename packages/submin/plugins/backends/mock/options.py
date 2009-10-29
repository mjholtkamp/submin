_options = {}

def clear_options():
	_options.clear()

def value(key):
	return _options[key]

def set_value(key, value):
	_options[key] = value

def options():
	return _options
