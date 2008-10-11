import unittest
from path import Path

class PathTests(unittest.TestCase):
	def testConcatPaths(self):
		p1 = Path("/home")
		p2 = Path("jeanpaul")
		self.assertEquals(str(p1 + p2), "/home/jeanpaul")

	def testConcatPathString(self):
		p1 = Path("/home")
		p2 = "jeanpaul"
		self.assertEquals(str(p1 + p2), "/home/jeanpaul")

	def testBasename(self):
		p = Path("/home/jeanpaul/test.file")
		self.assertEquals(p.basename(), "test.file")

	def testDirnameWithFile(self):
		p = Path("/home/jeanpaul/test.file")
		self.assertEquals(p.dirname(), "/home/jeanpaul")

	def testDirnameForFile(self):
		p = Path("/home/jeanpaul/", append_slash=True)
		self.assertEquals(p.dirname(), "/home/jeanpaul")

	def testDirnameForFileNoAppend(self):
		p = Path("/home/michiel")
		self.assertEquals(p.dirname(), "/home")

	def testConcatRelative(self):
		p1 = Path("/home")
		p2 = Path("/jeanpaul")
		self.assertEquals(str(p1 + p2), "/home/jeanpaul")

	def testAppendSlash(self):
		p1 = Path("/home", append_slash=True)
		p2 = Path("/jeanpaul")
		self.assertEquals(str(p1 + p2), "/home/jeanpaul/")

	def testStripSlash(self):
		p1 = Path("/home")
		p2 = Path("/jeanpaul/")
		self.assertEquals(str(p1 + p2), "/home/jeanpaul")

	def testStr(self):
		p = Path("/home/jeanpaul/")
		self.assertEquals(str(p), "/home/jeanpaul")

	def testAbsoluteFix(self):
		p = Path("home/michiel")
		self.assertEquals(str(p), "/home/michiel")

	def testRoot(self):
		p = Path("/")
		self.assertEquals(str(p), "/")

	def testRootAppendSlash(self):
		p = Path("/", append_slash=True)
		self.assertEquals(str(p), "/")

	def testPathJoin(self):
		p = Path("/base")
		username = "test"
		path = p + "/user/show/" + username
		self.assertEquals(str(path), "/base/user/show/test")

if __name__ == "__main__":
	unittest.main()
