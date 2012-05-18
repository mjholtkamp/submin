import unittest
import c_apacheconf

class SubminAdminApacheConfTests(unittest.TestCase):
	def testUrlPathEmpty(self):
		ac = c_apacheconf.c_apacheconf(None, [])
		result = ac.urlpath('')
		self.assertEquals(result, '/')

	def testUrlPathSlash(self):
		ac = c_apacheconf.c_apacheconf(None, [])
		result = ac.urlpath('/')
		self.assertEquals(result, '/')

	def testUrlPathFullURL(self):
		ac = c_apacheconf.c_apacheconf(None, [])
		result = ac.urlpath('http://www.example.com/')
		self.assertEquals(result, '/')

	def testUrlPathFullURLSubDir(self):
		ac = c_apacheconf.c_apacheconf(None, [])
		result = ac.urlpath('http://www.example.com/submin/help')
		self.assertEquals(result, '/submin/help/')

	def testUrlPathURLpath(self):
		ac = c_apacheconf.c_apacheconf(None, [])
		result = ac.urlpath('/submin/')
		self.assertEquals(result, '/submin/')

class SubminAdminElseTests(unittest.TestCase):
	def testSomethingelse(self):
		pass

if __name__ == "__main__":
	unittest.main()
