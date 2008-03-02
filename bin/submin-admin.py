#!/usr/bin/python

def main():
	from sys import argv, path
	import os
	path.append('_SUBMIN_LIB_DIR_')
	env = 'SUBMIN_LIB_DIR'
	if env in os.environ:
		path.append(os.environ[env])

	try:
		from subminadmin.subminadmin import SubminAdmin
	except ImportError, e:
		print e
		print "is environment %s set?" % env
		return

	try:
		a = SubminAdmin()
		a.run(argv)
	except KeyboardInterrupt:
		print

if __name__ == "__main__":
	main()
