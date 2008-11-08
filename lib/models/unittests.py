import unittest
from user import User, UserExists, NotAuthorized, InvalidEmail, addUser

class UserTests(unittest.TestCase):
	def setUp(self):
		addUser("test")

	def tearDown(self):
		User("test").remove()

	def testEmailSingleQuoteInvalid(self):
		u = User("test")
		self.assertRaises(InvalidEmail, u.setEmail, "a'@example.com")

	def testEmailDoubleQuoteInvalid(self):
		u = User("test")
		self.assertRaises(InvalidEmail, u.setEmail, 'a"@example.com')

	def testEmailDoubleDot(self):
		u = User("test")
		self.assertRaises(InvalidEmail, u.setEmail, "a@example..com")

	def testEmailDoubleAt(self):
		u = User("test")
		self.assertRaises(InvalidEmail, u.setEmail, "a@@example.com")

	def testEmailSimple(self):
		u = User("test")
		e = "a@a.a"
		u.setEmail(e)
		self.assertEquals(e, u.getEmail())

	def testEmailEndingDotOk(self):
		u = User("test")
		e = "a@a.a."
		u.setEmail(e)
		self.assertEquals(e, u.getEmail())

	def testEmailIPAddressOK(self):
		u = User("test")
		e = "a@999.999.999.999"
		u.setEmail(e)
		self.assertEquals(e, u.getEmail())

	def testEmailUserPlusOk(self):
		u = User("test")
		e = "a+b@example.com"
		u.setEmail(e)
		self.assertEquals(e, u.getEmail())

if __name__ == "__main__":
	import os, tempfile
	tempfile.tempdir = "/tmp"
	tempfile.template = "submin"
	config_file = tempfile.mktemp()
	authz_file = tempfile.mktemp()
	userprop_file = tempfile.mktemp()
	access_file = tempfile.mktemp()
	
	os.environ['SUBMIN_CONF'] = config_file
	config_content = """
[svn]
authz_file = %s
userprop_file = %s
access_file = %s
repositories = /tmp/svn

[www]
base_url = /

""" % (authz_file, userprop_file, access_file)
	file(config_file, 'w').write(config_content)

	unittest.main()
	
	for f in [config_file, authz_file, userprop_file, access_file]:
		os.unlink(f)
