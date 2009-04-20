import unittest
import os
from user import User, UserExists, NotAuthorized, InvalidEmail, InvalidFullName, addUser, listUsers
from config.authz.authz import UnknownUserError
from config.config import Config

from repository import listRepositories, repositoriesOnDisk, Repository

class UserTests(unittest.TestCase):
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

		self.repositories = ['repos']
		for r in self.repositories:
			os.system("svnadmin create '%s'" % os.path.join(self.reposdir, r))

		addUser("test")

	def tearDown(self):
		User("test").remove()
		
		for f in [self.config_file, self.authz_file, self.userprop_file, self.access_file]:
			f.close()

		os.system("rm -rf '%s'" % self.reposdir)

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

	def testListUsersAdmin(self):
		class MockUser():
			is_admin = True

		mock_user = MockUser()
		
		addUser("foo")
		users = [x.name for x in listUsers(mock_user)]
		users.sort()
		self.assertEquals(users, ["foo", "test"])

	def testListUsersNonAdmin(self):
		class MockUser():
			is_admin = False
			name = "foo"

		mock_user = MockUser()

		addUser("foo")
		users = [x.name for x in listUsers(mock_user)]
		users.sort()
		self.assertEquals(users, ["foo"])

	def testFullName(self):
		expected_full_name = "Full Name"
		u = User("test")
		full = u.getFullName()
		self.assertEquals(full, "")
		u.setFullName(expected_full_name)
		full = u.getFullName()
		self.assertEquals(full, expected_full_name)

	def testInvalidFullName(self):
		u = User("test")
		invalid_chars = '\'"\n'
		for invalid_char in invalid_chars.split():
			self.assertRaises(InvalidFullName, u.setFullName, invalid_char)

	def testSaveNotificationsAdmin(self):
		u = User("test")
		u.setNotification("repos", {"allowed": True, "enabled": True}, True)
		u.setNotification("non-existing", {"allowed": True, "enabled": True}, True)
		u.saveNotifications()
		u2 = User("test")
		self.assertEquals(u2.notifications.has_key("repos"), True)
		self.assertEquals(u2.notifications["repos"]["allowed"], True)
		self.assertEquals(u2.notifications["repos"]["enabled"], True)
		# should not have notification for non-existing repository
		self.assertEquals(u2.notifications.has_key("non-existing"), False)

	def testSaveNotificationsNonAdminNotAllowed(self):
		"""If not allowed, should raise NotAuthorized"""
		u = User("test")
		self.assertRaises(NotAuthorized, u.setNotification, "repos", {"allowed": True, "enabled": True}, False)

	def testSaveNotificationsNonAdminAllowed(self):
		"""First set allowed as admin, then set enabled as user"""
		u = User("test")
		u.setNotification("repos", {"allowed": True, "enabled": False}, True)
		u.setNotification("repos", {"allowed": True, "enabled": True}, False)
		u.saveNotifications()
		u2 = User("test")
		self.assertEquals(u2.notifications.has_key("repos"), True)
		self.assertEquals(u2.notifications["repos"]["allowed"], True)
		self.assertEquals(u2.notifications["repos"]["enabled"], True)

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

[backend]
bindir = /bin

		""" % (self.authz_file.name, self.userprop_file.name, \
			self.access_file.name, self.reposdir)

		self.config_file.write(config_content)
		self.config_file.flush() # but keep it open!

		# this is so config loads the new config file, it's a Singleton!
		Config().reinit()

		# now make some repositories
		self.repositories = ['foo', 'BAR', 'removeme', 'invalidperm', \
			'invalidperm2', 'subdirs']
		for r in self.repositories:
			os.system("svnadmin create '%s'" % os.path.join(self.reposdir, r))

		os.system("chmod 000 '%s'" % \
			os.path.join(self.reposdir, 'invalidperm'))

		os.system("chmod 000 '%s'" % \
			os.path.join(self.reposdir, 'invalidperm2', 'db', 'revs'))

	def tearDown(self):
		for f in [self.config_file, self.authz_file, self.userprop_file, self.access_file]:
			f.close()

		os.system("chmod 777 '%s'" % os.path.join(self.reposdir, 'invalidperm'))
		os.system("chmod 777 '%s'" % \
			os.path.join(self.reposdir, 'invalidperm2', 'db', 'revs'))
		os.system("rm -rf '%s'" % self.reposdir)

	def testRepositoriesOnDisk(self):
		result = repositoriesOnDisk()
		result.sort()
		copy = self.repositories[:]
		copy.sort()
		self.assertEquals(result, copy)

	def testListRepositoriesAll(self):
		"""Test listRepositories, which checks for valid permissions of repositories"""
		class MockUser():
			is_admin = True

		mock_user = MockUser()
		result = listRepositories(mock_user, only_invalid=False)
		copy = self.repositories[:]
		copy.sort()
		copy.remove('invalidperm')
		copy.remove('invalidperm2')
		self.assertEquals(result, copy)

	def testListRepositoriesOnlyInvalid(self):
		"""Test listRepositories, which checks for valid permissions of repositories"""
		class MockUser():
			is_admin = True

		mock_user = MockUser()
		result = listRepositories(mock_user, only_invalid=True)
		expected_result = ['invalidperm', 'invalidperm2']
		self.assertEquals(result, expected_result)

	def testExistingRepository(self):
		r = Repository('foo')
		self.assertEquals(str(r), 'foo')

	def testInvalidPermRepository(self):
		self.assertRaises(Repository.PermissionDenied, Repository, "invalidperm")

	def testInvalidPermRepository2(self):
		self.assertRaises(Repository.PermissionDenied, Repository, "invalidperm2")

	def testUnknownRepository(self):
		self.assertRaises(Repository.DoesNotExist, Repository, "non-existing-repository")

	def testHasSubDirs(self):
		for subdir in ['test', 'test/subdir']:
			os.system("svn mkdir -m '' file://'%s' >/dev/null" % \
				os.path.join(self.reposdir, 'subdirs', subdir))
		r = Repository('subdirs')
		self.assertEquals(r.hassubdirs('test'), True)

	def testSubDirsContents(self):
		for subdir in ['test', 'test/subdir', 'nosubdirs']:
			os.system("svn mkdir -m '' file://'%s' >/dev/null" % \
				os.path.join(self.reposdir, 'subdirs', subdir))
		r = Repository('subdirs')
		result = r.getsubdirs('')
		expected_result = [{'has_subdirs': False, 'name': u'nosubdirs'}, \
			{'name': u'test', 'has_subdirs': True}]

		result.sort()
		expected_result.sort()
		self.assertEquals(result, expected_result)

	def testRemoveRepository(self):
		r = Repository('removeme')
		r.remove()
		result = repositoriesOnDisk()
		copy = self.repositories[:]
		for res in result:
			copy.remove(res)

		self.assertEquals(['removeme'], copy)

	def testChangeNotificationsEmptyHook(self):
		expected_hook = '''#!/bin/sh
### SUBMIN AUTOCONFIG, DO NOT ALTER FOLLOWING LINE ###
/usr/bin/python /bin/post-commit.py "%s" "$1" "$2"
''' % self.config_file.name
		hook_fname = os.path.join(self.reposdir, 'BAR', 'hooks', 'post-commit')

		r = Repository('BAR')
		r.changeNotifications(enable=True)
		hook = ''.join(file(hook_fname, 'r').readlines())
		self.assertEquals(hook, expected_hook)

	def testChangeNotificationsExistingHook(self):
		expected_hook1 = '''#!/bin/sh
# just a comment
### SUBMIN AUTOCONFIG, DO NOT ALTER FOLLOWING LINE ###
/usr/bin/python /bin/post-commit.py "%s" "$1" "$2"
''' % self.config_file.name
		expected_hook2 = '''#!/bin/sh
# just a comment
'''
		hook_fname = os.path.join(self.reposdir, 'BAR', 'hooks', 'post-commit')
		file(hook_fname, 'w').write(expected_hook2)

		r = Repository('BAR')
		r.changeNotifications(enable=True)
		hook = ''.join(file(hook_fname, 'r').readlines())
		self.assertEquals(hook, expected_hook1)
		r.changeNotifications(enable=False)
		hook = ''.join(file(hook_fname, 'r').readlines())
		self.assertEquals(hook, expected_hook2)

	def testNotificationsEnabled(self):
		r = Repository('BAR')
		# first time, because no file is present
		self.assertEquals(r.notificationsEnabled(), False)
		r.changeNotifications(enable=True)
		self.assertEquals(r.notificationsEnabled(), True)
		# a second time, because now a file is created
		r.changeNotifications(enable=False)
		self.assertEquals(r.notificationsEnabled(), False)

if __name__ == "__main__":
	unittest.main()
