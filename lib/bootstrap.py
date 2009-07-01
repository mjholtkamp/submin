import os

def fimport(filename, fromlist=[]):
	return __import__(filename, globals(), locals(), fromlist)

if not os.environ.has_key('SUBMIN_SETTINGS'):
	raise Exception('Settings cannot be imported, please set the SUBMIN_SETTINGS environment variable ')

settings = fimport(os.environ['SUBMIN_SETTINGS'])
