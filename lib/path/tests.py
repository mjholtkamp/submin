import unittest
from path import Path

class PathTests(unittest.TestCase):
	def testConcatPaths(self):
		p1 = Path("/home")
		p2 = Path("jeanpaul")
		self.assertEquals(p1 + p2, "/home/jeanpaul")

	def testConcatPathString(self):
		p1 = Path("/home")
		p2 = "jeanpaul"
		self.assertEquals(p1 + p2, "/home/jeanpaul")

	def testBasename(self):
		p = Path("/home/jeanpaul/test.file")
		self.assertEquals(p.basename(), "test.file")

	def testDirnameWithFile(self):
		p = Path("/home/jeanpaul/test.file")
		self.assertEquals(p.dirname(), "/home/jeanpaul")

	def testDirnameForFile(self):
		p = Path("/home/jeanpaul/")
		self.assertEquals(p.dirname(), "/home/jeanpaul")

	def testConcatRelative(self):
		p1 = Path("/home")
		p2 = Path("/jeanpaul")
		self.assertEquals(p1 + p2, "/home/jeanpaul")

	def testAppendSlash(self):
		p1 = Path("/home", append_slash=True)
		p2 = Path("/jeanpaul")
		self.assertEquals(p1 + p2, "/home/jeanpaul/")

	def testStripSlash(self):
		p1 = Path("/home")
		p2 = Path("/jeanpaul/")
		self.assertEquals(p1 + p2, "/home/jeanpaul")

if __name__ == "__main__":
	unittest.main()
