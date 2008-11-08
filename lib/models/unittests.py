import unittest
import os
from user import User, UserExists, NotAuthorized, InvalidEmail, addUser
from config.config import Config

class UserTests(unittest.TestCase):
	def setUp(self):
		import tempfile
		self.config_file = tempfile.NamedTemporaryFile(dir="/tmp/", prefix="submin_cfg_")
		self.authz_file = tempfile.NamedTemporaryFile(dir="/tmp/", prefix="submin_authz_")
		self.userprop_file = tempfile.NamedTemporaryFile(dir="/tmp/", prefix="submin_userprop_")
		self.access_file = tempfile.NamedTemporaryFile(dir="/tmp/", prefix="submin_access_file_")

		os.environ['SUBMIN_CONF'] = self.config_file.name
		config_content = """
[svn]
authz_file = %s
userprop_file = %s
access_file = %s
repositories = /tmp/svn

[www]
base_url = /

		""" % (self.authz_file.name, self.userprop_file.name, self.access_file.name)
		self.config_file.write(config_content)
		self.config_file.flush() # but keep it open!

		# this is so config loads the new config file, it's a Singleton!
		Config().reinit()

		addUser("test")

	def tearDown(self):
		User("test").remove()
		
		for f in [self.config_file, self.authz_file, self.userprop_file, self.access_file]:
			f.close()

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
	unittest.main()
