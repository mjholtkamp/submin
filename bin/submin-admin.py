#!/usr/bin/python

if __name__ == "__main__":
	from sys import argv, path
	path.append('_SUBMIN_LIB_DIR_')
	path.append('/var/www/submin/lib')
	from subminadmin.subminadmin import SubminAdmin

	try:
		a = SubminAdmin()
		a.run(argv)
	except KeyboardInterrupt:
		print

