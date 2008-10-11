import os
import commands

def main():
	cmd = "find lib -name unittests.py"
	(exitstatus, outtext) = commands.getstatusoutput(cmd)
	for file in outtext.split('\n'):
		os.system("PYTHONPATH=lib python %s" % file)

if __name__ == "__main__":
	main()
