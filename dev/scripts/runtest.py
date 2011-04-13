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

		# ignore never executed statements
		cov.exclude("if False:")
		cov.exclude('if __name__ == .__main__.:')
		cov.exclude('unittest.main()') # is not used since we build our own suite
	except ImportError, e:
		print "No coverage reports available."
		use_coverage = False
else:
	# Remove the --no-coverage option from the sys.argv array to facilitate the
	# supplying of search paths below.
	idx = sys.argv.index("--no-coverage")
	del sys.argv[idx]

def main():
	libprefix = "packages"
	paths = libprefix
	if len(sys.argv) > 1:
		paths = ''
		for path in sys.argv[1:]:
			paths += "%s " % (path.startswith(libprefix) and path or os.path.join(libprefix, path))

	cmd = "find %s -name unittests.py" % paths
	(exitstatus, outtext) = commands.getstatusoutput(cmd)

	# Most modules assume they have lib in the import-path.
	sys.path.insert(0, libprefix)

	if use_coverage:
		cov.start() # Starting here to avoid bin/runtest to show up in coverage-report

	suite = unittest.TestSuite()
	for file in outtext.split('\n'):
		file = os.path.normpath(file)
		print "Adding %s to the test-suite" % file

		# transform filename to module name
		modname = file.replace('/', '.')[len(libprefix + "."):-3] # skip `libprefix.', up till `.py'
		module = __import__(modname, [], [], '.'.join(modname.split('.')[:-1]))
		if hasattr(module, 'suite'):
			suite.addTest(module.suite())
		else:
			suite.addTest(
					unittest.defaultTestLoader.loadTestsFromModule(module))

	# Run the test!
	testresult = unittest.TextTestRunner(verbosity=1).run(suite)

	if use_coverage:
		cov.stop()
		cov.report(show_missing=False,
			omit_prefixes=["/usr/lib/", "/opt", "/System/Library/", "/Library/Python/"])
		cov.annotate(directory="coverage-annotate")
		print "Coverage annotations are stored in `coverage-annotate/'"

	# Provide a non-zero exitstatus when tests fail.
	if not testresult.wasSuccessful():
		sys.exit(1)

if __name__ == "__main__":
	main()
