import os
import commands
import sys
import unittest

if "--help" in sys.argv or "-h" in sys.argv:
	print "Usage: %s [--no-coverage] [--help|-h]" % sys.argv[0]
	print
	print "Options:"
	print "    --no-coverage: Don't display coverage report and don't annotate"
	print "    --help (-h):   Display this help-text"
	print
	print "%s looks for unittests (in files named unittests.py) in the " % sys.argv[0]
	print "`lib/' directory."
	print "To narrow the search, supply a sub-directory of `lib/' at the commandline"
	print
	print "By default, %s displays coverage report if it is able to load the" % sys.argv[0]
	print "coverage-module. Annotations are stored in the `coverage-annotate/' directory."
	sys.exit(0)

use_coverage = False
cov = None
if "--no-coverage" not in sys.argv:
	try:
		import coverage
		use_coverage = True
		cov = coverage.coverage()
		cov.start()
	except ImportError, e:
		print "No coverage reports available."
		use_coverage = False
else:
	# Remove the --no-coverage option from the sys.argv array to facilitate the
	# supplying of search paths below.
	idx = sys.argv.index("--no-coverage")
	del sys.argv[idx]

def main():
	paths = "lib"
	if len(sys.argv) > 1:
		paths = ''
		for path in sys.argv[1:]:
			paths += "%s " % (path.startswith("lib") and path or os.path.join("lib", path))

	cmd = "find %s -name unittests.py" % paths
	(exitstatus, outtext) = commands.getstatusoutput(cmd)

	# Most modules assume they have lib in the import-path.
	sys.path.insert(0, "lib")

	suite = unittest.TestSuite()
	for file in outtext.split('\n'):
		file = os.path.normpath(file)
		print "Adding %s to the test-suite" % file

		# transform filename to module name
		mod = file.replace('/', '.')[4:-3] # skip `lib.', up till `.py'
		suite.addTest(unittest.defaultTestLoader.loadTestsFromName(mod))

	# Run the test!
	unittest.TextTestRunner(verbosity=1).run(suite)

	if use_coverage:
		cov.stop()
		cov.report(show_missing=False,
			omit_prefixes=["/usr/lib/", "/System/Library/", "/Library/Python/"])
		cov.annotate(directory="coverage-annotate")
		print "Coverage annotations are stored in `coverage-annotate/'"

if __name__ == "__main__":
	main()
