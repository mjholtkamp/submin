import unittest
import subprocess
from common import execute
from common import osutils

class ExecuteTests(unittest.TestCase):
	def testOutput(self):
		output = execute.check_output(["/bin/echo", "test321"])
		self.assertEquals(output, "test321\n")

	def testFalse(self):
		self.assertRaises(subprocess.CalledProcessError, execute.check_output, ["/bin/false"])

	def testTrue(self):
		execute.check_output(["/bin/true"])

class OSUtils(unittest.TestCase):
	def testMkDirs(self):
		osutils.mkdirs('/tmp/')

if __name__ == "__main__":
	unittest.main()
