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
	cmd = "find lib -name unittests.py"
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
		os.system("rm -rf coverage-tmp")

if __name__ == "__main__":
	main()
