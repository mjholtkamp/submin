# Convenience functions around os related functions
import os
import errno

def mkdirs(name, mode=0777):
	"""Wrapper around os.makedirs().
	This elimiates the need to catch exception if the dir already exists"""
	try:
		os.makedirs(name, mode)
	except OSError, e:
		if e.errno == errno.EEXIST:
			return

		raise
