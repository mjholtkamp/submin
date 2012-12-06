import os
import sys
import re
import inspect

import unittest

def find_unittest_modules():
	tests_dir = os.path.join(os.path.dirname(__file__), 'tests')
	for (path, dirs, files) in os.walk(tests_dir):
		for f in files:
			for match in re.findall('^(.*)\.py$', f):
				if match == "__init__":
					continue

				module_path = "submin.models.tests.%s" % (match,)
				module = __import__(module_path)
				for clsname, cls in inspect.getmembers(sys.modules[module_path], inspect.isclass):
					if cls.__module__ == module_path and clsname.endswith('Tests'):
						yield "%s.%s" % (module_path, clsname)

def suite():
	s = unittest.TestSuite()
	subtests = find_unittest_modules()
	map(s.addTest, map(unittest.defaultTestLoader.loadTestsFromName, subtests))
	return s

if __name__ == "__main__":
	unittest.main()
