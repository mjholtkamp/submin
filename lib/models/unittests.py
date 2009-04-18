import unittest
import os
from user import User, UserExists, NotAuthorized, InvalidEmail, addUser
from config.authz.authz import UnknownUserError
from config.config import Config

from repository import listRepositories, repositoriesOnDisk, Repository

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

	def testPassword(self):
		u = User("test")
		u.setPassword("foobar")
		config = Config()
		self.assertEquals(config.htpasswd.check("test", "foobar"), True)

	def testAddDoubleUser(self):
		self.assertRaises(UserExists, addUser, "test")

	def testUnknownUser(self):
		self.assertRaises(UnknownUserError, User, "not a user")

	def testUserName(self):
		u = User("test")
		self.assertEquals(str(u), "test")

	def testNotAdmin(self):
		u = User("test")
		self.assertRaises(NotAuthorized, u.setNotification, "repos", dict(allowed=True, enabled=True), False)

	# def testSaveNotifications(self):
	# 	import time
	# 	u = User("test")
	# 	u.setNotification("repos", {"allowed": True, "enabled": True}, True)
	# 	time.sleep(1.1) # file has to be saved, time check resolution is 1 second
	# 	u.saveNotifications()
	# 	u2 = User("test")
	# 	print u2.notifications
	# 	self.assertEquals(u2.notifications.has_key("repos"), True)
	# 	self.assertEquals(u2.notifications["repos"]["allowed"], True)
	# 	self.assertEquals(u2.notifications["repos"]["enabled"], True)


class RepositoryTests(unittest.TestCase):
	def setUp(self):
		import tempfile
		self.reposdir = tempfile.mkdtemp()
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
repositories = %s

[www]
base_url = /

		""" % (self.authz_file.name, self.userprop_file.name, \
			self.access_file.name, self.reposdir)

		self.config_file.write(config_content)
		self.config_file.flush() # but keep it open!

		# this is so config loads the new config file, it's a Singleton!
		Config().reinit()

		# now make some repositories
		self.repositories = ['test1', 'foo', 'BAR', 'removeme']
		for r in self.repositories:
			os.system("svnadmin create %s" % os.path.join(self.reposdir, r))

	def tearDown(self):
		for f in [self.config_file, self.authz_file, self.userprop_file, self.access_file]:
			f.close()

		os.system("rm -rf '%s'" % self.reposdir)

	def testRepositoriesOnDisk(self):
		result = repositoriesOnDisk()
		self.assertEquals(result.sort(), self.repositories.sort())

	def testExistingRepository(self):
		r = Repository(self.repositories[0])
		self.assertEquals(str(r), self.repositories[0])

	def testUnknownRepository(self):
		self.assertRaises(Repository.DoesNotExist, Repository, "non-existing-repository")

	def testRemoveRepository(self):
		r = Repository('removeme')
		r.remove()
		result = repositoriesOnDisk()
		copy = self.repositories[:]
		for res in result:
			copy.remove(res)

		self.assertEquals(['removeme'], copy)

if __name__ == "__main__":
	unittest.main()
