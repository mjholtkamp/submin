import os
import commands
import sys

def which(filename):
	if not os.environ.has_key('PATH') or os.environ['PATH'] == '':
		p = os.defpath
	else:
		p = os.environ['PATH']

	pathlist = p.split (os.pathsep)

	for path in pathlist:
		f = os.path.join(path, filename)
		if os.access(f, os.X_OK):
			return f
	return None

def main():
	paths = "lib"
	if len(sys.argv) > 1:
		paths = map(os.path.join, ["lib"], sys.argv[1:])
		paths = ' '.join(paths)

	cmd = "find %s -name unittests.py" % paths
	(exitstatus, outtext) = commands.getstatusoutput(cmd)
	use_coverage = False
	python_cmd = "python"

	for pc in ["python-coverage", "coverage"]:
		if which(pc):
			use_coverage = True
			python_cmd = pc

	if use_coverage:
		os.environ['COVERAGE_FILE'] = "coverage-tmp/.converage"
		try:
			os.mkdir("coverage-tmp")
			os.mkdir("coverage-annotate")
		except OSError:
			pass

	for file in outtext.split('\n'):
		print("running %s" % file)
		options = ""
		if use_coverage:
			options = "-x -p"

		os.system("PYTHONPATH=lib %s %s %s" % (python_cmd, options, file))

	if use_coverage:
		os.system("%s -c" % python_cmd)
		os.system("%s -r -o /usr/lib,/System/Library/" % python_cmd)
		omit = ["/usr/lib", "/System/Library"]
		# touch coverage.py, it tries to find itself while annotating, sigh
		open("coverage.py", "w")
		open("pmock.py", "w")
		os.system("%s -a -o %s -d coverage-annotate" % (python_cmd, ','.join(omit)))
		os.system("rm -rf coverage-tmp coverage.py pmock.py")

if __name__ == "__main__":
	main()
