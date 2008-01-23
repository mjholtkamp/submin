#!/usr/bin/python

if __name__ == "__main__":
	from sys import argv, path
	path.append('/usr/share/submin/lib')
	from subminadmin.subminadmin import SubminAdmin

	try:
		a = SubminAdmin()
		a.run(argv)
	except KeyboardInterrupt:
		print

