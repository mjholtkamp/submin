# Logging module. Wanting this to be simpler then the logging module in the
# standard library.

import sys
import time

class Log:
	levels = ['Submerge']
	fp = None

	def __init__(self, _file=sys.stdout):
		if not Log.fp:
			try:
				Log.fp = _file
				Log.fp.write
			except:
				Log.fp = file(_file, 'a+')

	def write(self, ip, message, level=0):
		self.fp.write('%s - [%s] %s - %s\n' % 
				(ip, time.asctime(), self.levels[level], message))
		self.fp.flush()


def open(filename):
	"""Opens filename for logging
	@returns Log instance"""
	logger = Log(filename)
	return logger

def log(ip, message, level=0):
	"""Logs message to file"""
	logger = Log()
	logger.write(ip, message, int(level))

def addlevel(levelname):
	"""Adds a level to the level-list"""
	Log.levels.append(levelname)
	return (len(Log.levels) - 1)

def levels():
	"""@returns levels"""
	return Log.levels
