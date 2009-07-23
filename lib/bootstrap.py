import os, sys

def fimport(filename, fromlist=[]):
	return __import__(filename, globals(), locals(), fromlist)

if not os.environ.has_key('SUBMIN_ENV'):
	raise Exception('Settings cannot be imported, please set the SUBMIN_ENV' +\
	' environment variable to the submin base directory')

sys.path.insert(0, os.path.join(os.environ['SUBMIN_ENV'], 'conf'))

settings = fimport('settings')

del sys.path[0]
