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
		p = Path("/home/jeanpaul/", append_slash=True)
		self.assertEquals(p.dirname(), "/home/jeanpaul")

	def testDirnameForFileNoAppend(self):
		p = Path("/home/michiel")
		self.assertEquals(p.dirname(), "/home")

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

	def testStr(self):
		p = Path("/home/jeanpaul/")
		self.assertEquals(p, "/home/jeanpaul")

	def testAbsoluteFix(self):
		p = Path("home/michiel", absolute=True)
		self.assertEquals(p, "/home/michiel")

	def testRoot(self):
		p = Path("/")
		self.assertEquals(p, "/")

	def testRootAppendSlash(self):
		p = Path("/", append_slash=True)
		self.assertEquals(p, "/")

	def testPathJoin(self):
		p = Path("/base")
		username = "test"
		path = p + "/user/show/" + username
		self.assertEquals(path, "/base/user/show/test")
		
	def testRawCopy(self):
		p = Path("/base")
		p2 = p.copy()
		self.assertEquals(p, p2)

	def testNotAbsolute(self):
		p = Path("notabsolute", absolute=False)
		self.assertEquals(p, "notabsolute")

	def testStringInheritence(self):
		p = Path("/home/michiel")
		self.assertEquals(p, "/home/michiel")

	def testUnicode(self):
		moon = u'\u6708'
		sun = u'\u65e5'
		p = Path(moon)
		self.assertEquals(p + sun, moon + '/' + sun)

	def testStrAndUnicode(self):
		moon = 'moon'
		sun = u'\u65e5'
		p = Path(moon)
		self.assertEquals(p + sun, moon + '/' + sun)

if __name__ == "__main__":
	unittest.main()
