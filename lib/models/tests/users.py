import unittest
import shutil # for temporary dir
import tempfile # for temporary dir
from pmock import *

mock_settings = Mock()
mock_settings.backend = "mock"
mock_settings.base_dir = "/"

from models import backend
from models.user import User
from models.options import Options
from models.exceptions import UserExistsError, UnknownUserError, UserPermissionError
from models.validators import *
from models.repository import Repository

class UserTests(unittest.TestCase):
	def setUp(self):
		backend.open(mock_settings)
		User.add("test")
		self.u = User("test")
		self.o = Options()
		self.tmp_dirs = []

	def tearDown(self):
		self.u.remove()
		backend.close()
		for tmp_dir in self.tmp_dirs:
			shutil.rmtree(tmp_dir)

	def makeTempDir(self):
		tmp_dir = tempfile.mkdtemp(prefix="tmp-%s-" % self.__class__.__name__)
		self.tmp_dirs.append(tmp_dir)
		return tmp_dir

	def addRepository(self, reposname):
		svndir = self.makeTempDir()
		self.o.set_value('svn_dir', svndir)
		Repository.add('svn', reposname)

	def setEmail(self, u, email):
		u.email = email

	def setUsername(self, u, username):
		u.name = username

	def setFullname(self, u, fullname):
		u.fullname = fullname

	def testEmailSingleQuoteInvalid(self):
		self.assertRaises(InvalidEmail, self.setEmail, self.u, "a'@example.com")

	def testEmailDoubleQuoteInvalid(self):
		self.assertRaises(InvalidEmail, self.setEmail, self.u, 'a"@example.com')

	def testEmailDoubleDot(self):
		self.assertRaises(InvalidEmail, self.setEmail, self.u, "a@example..com")

	def testEmailDoubleAt(self):
		self.assertRaises(InvalidEmail, self.setEmail, self.u, "a@@example.com")

	def testEmailSimple(self):
		e = "a@a.a"
		self.u.email = e
		self.assertEquals(e, self.u.email)

	def testEmailEndingDotOk(self):
		e = "a@a.a."
		self.u.email = e
		self.assertEquals(e, self.u.email)

	def testEmailIPAddressOK(self):
		e = "a@999.999.999.999"
		self.u.email = e
		self.assertEquals(e, self.u.email)

	def testEmailUserPlusOk(self):
		e = "a+b@example.com"
		self.u.email = e
		self.assertEquals(e, self.u.email)

	def testPassword(self):
		self.u.set_password("foobar")
		self.assertTrue(self.u.check_password("foobar"))

	def testAddDoubleUser(self):
		self.assertRaises(UserExistsError, User.add, "test")

	def testUnknownUser(self):
		self.assertRaises(UnknownUserError, User, "not a user")

	def testUserName(self):
		self.assertEquals(str(self.u), "test")

	def testNotAdmin(self):
		self.assertRaises(UserPermissionError, self.u.set_notification, "repos", True, True, self.u)

	def testListUsersAdmin(self):
		mock_user = Mock()
		mock_user.is_admin = True
		User.add("foo")
		users = [x for x in User.list(mock_user)]
		users.sort()
		self.assertEquals(users, ["foo", "test"])

	def testListUsersNonAdmin(self):
		mock_user = Mock()
		mock_user.is_admin = False
		mock_user.name = "foo"
		User.add("foo")
		users = [x for x in User.list(mock_user)]
		users.sort()
		self.assertEquals(users, ["foo"])

	def testRemoveUser(self):
		mock_user = Mock()
		mock_user.is_admin = True
		User.add("foo")
		foo = User("foo")
		foo.remove()
		self.assert_("foo" not in [x for x in User.list(mock_user)])

	def testUserName(self):
		self.assertEquals(self.u.name, "test")

	def testSetUserName(self):
		self.u.name = "foo"
		self.assertEquals(self.u.name, "foo")

	def testInvalidUserName(self):
		invalid_chars = '\'"\n'
		for invalid_char in invalid_chars:
			self.assertRaises(InvalidUsername, self.setUsername, self.u,
					invalid_char)

	def testFullName(self):
		expected_full_name = "Full Name"
		self.u.fullname = expected_full_name
		self.assertEquals(self.u.fullname, expected_full_name)

	def testInvalidFullName(self):
		invalid_chars = '\'"\n'
		for invalid_char in invalid_chars.split():
			self.assertRaises(InvalidFullname, self.setFullname, self.u,
					invalid_char)

	def testSetIsAdmin(self):
		self.assertFalse(self.u.is_admin)
		self.u.is_admin = True
		self.assertTrue(self.u.is_admin)
		self.u.is_admin = False
		self.assertFalse(self.u.is_admin)

	def testSaveNotificationsAdmin(self):
		self.addRepository('repos') # otherwise, we cannot add notifications
		mock_admin = Mock()
		mock_admin.is_admin = True
		self.u.set_notification("repos", True, True, mock_admin)
		self.u.set_notification("non-existing", True, True, mock_admin)
		u2 = User("test")
		notifications = u2.notifications()
		self.assertTrue(notifications['repos']['enabled'])
		# should not have notification for non-existing repository
		self.assertFalse(notifications.has_key("non-existing"))

	def testSaveNotificationsNonAdminNotAllowed(self):
		"""If not allowed, should raise Exception"""
		# default permissions are set to false
		self.assertRaises(UserPermissionError, self.u.set_notification, "repos", True, True, self.u)

	def testSaveNotificationsNonAdminAllowed(self):
		"""First set allowed as admin, then set enabled as user"""
		self.addRepository('repos') # otherwise, we cannot add notifications
		mock_admin = Mock()
		mock_admin.is_admin = True
		self.u.set_notification("repos", True, False, mock_admin)
		notifications = self.u.notifications()
		self.assertFalse(notifications["repos"]["enabled"])
		self.u.set_notification("repos", True, True, self.u)
		notifications = self.u.notifications()
		self.assertTrue(notifications["repos"]["enabled"])
		

