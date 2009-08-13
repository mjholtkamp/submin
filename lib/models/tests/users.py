import unittest
from pmock import *

mock_settings = Mock()
mock_settings.backend = "mock"

from models import backendOpen, backendSetup, backendClose
from models.user import User, UserExistsError, UnknownUserError

from models.validators import *

class UserTests(unittest.TestCase):
	def setUp(self):
		backendOpen(mock_settings)
		User.add("test")

	def tearDown(self):
		backendClose()

	def setEmail(self, u, email):
		u.email = email

	def setUsername(self, u, username):
		u.name = username

	def setFullname(self, u, fullname):
		u.fullname = fullname

	def testEmailSingleQuoteInvalid(self):
		u = User("test")
		self.assertRaises(InvalidEmail, self.setEmail, u, "a'@example.com")

	def testEmailDoubleQuoteInvalid(self):
		u = User("test")
		self.assertRaises(InvalidEmail, self.setEmail, u, 'a"@example.com')

	def testEmailDoubleDot(self):
		u = User("test")
		self.assertRaises(InvalidEmail, self.setEmail, u, "a@example..com")

	def testEmailDoubleAt(self):
		u = User("test")
		self.assertRaises(InvalidEmail, self.setEmail, u, "a@@example.com")

	def testEmailSimple(self):
		u = User("test")
		e = "a@a.a"
		u.email = e
		self.assertEquals(e, u.email)

	def testEmailEndingDotOk(self):
		u = User("test")
		e = "a@a.a."
		u.email = e
		self.assertEquals(e, u.email)

	def testEmailIPAddressOK(self):
		u = User("test")
		e = "a@999.999.999.999"
		u.email = e
		self.assertEquals(e, u.email)

	def testEmailUserPlusOk(self):
		u = User("test")
		e = "a+b@example.com"
		u.email = e
		self.assertEquals(e, u.email)

	def testPassword(self):
		u = User("test")
		u.set_password("foobar")
		self.assertTrue(u.check_password("foobar"))

	def testAddDoubleUser(self):
		self.assertRaises(UserExistsError, User.add, "test")

	def testUnknownUser(self):
		self.assertRaises(UnknownUserError, User, "not a user")

	def testUserName(self):
		u = User("test")
		self.assertEquals(str(u), "test")

	def testNotAdmin(self):
		u = User("test")
		self.assertRaises(NotAuthorized, u.setNotification, "repos", dict(allowed=True, enabled=True), False)

	def testListUsersAdmin(self):
		mock_user = Mock()
		mock_user.is_admin = True
		User.add("foo")
		users = [x.name for x in User.list(mock_user)]
		users.sort()
		self.assertEquals(users, ["foo", "test"])

	def testListUsersNonAdmin(self):
		mock_user = Mock()
		mock_user.is_admin = False
		mock_user.name = "foo"
		User.add("foo")
		users = [x.name for x in User.list(mock_user)]
		users.sort()
		self.assertEquals(users, ["foo"])

	def testRemoveUser(self):
		mock_user = Mock()
		mock_user.is_admin = True
		User.add("foo")
		foo = User("foo")
		foo.remove()
		self.assert_("foo" not in [x.name for x in User.list(mock_user)])

	def testUserName(self):
		u = User("test")
		self.assertEquals(u.name, "test")

	def testSetUserName(self):
		u = User("test")
		u.name = "foo"
		self.assertEquals(u.name, "foo")

	def testInvalidUserName(self):
		u = User("test")
		invalid_chars = '\'"\n'
		for invalid_char in invalid_chars:
			self.assertRaises(InvalidUsername, self.setUsername, u,
					invalid_char)

	def testFullName(self):
		expected_full_name = "Full Name"
		u = User("test")
		u.fullname = expected_full_name
		self.assertEquals(u.fullname, expected_full_name)

	def testInvalidFullName(self):
		u = User("test")
		invalid_chars = '\'"\n'
		for invalid_char in invalid_chars.split():
			self.assertRaises(InvalidFullname, self.setFullname, u,
					invalid_char)

	def testIsAdmin(self):
		u = User("test")
		self.assert_(not u.is_admin)
		u.is_admin = True
		self.assert_(u.is_admin)

	def testSaveNotificationsAdmin(self):
		u = User("test")
		u.setNotification("repos", {"allowed": True, "enabled": True}, True)
		u.setNotification("non-existing", {"allowed": True, "enabled": True}, True)
		u.saveNotifications()
		u2 = User("test")
		self.assertTrue(u2.notifications.has_key("repos"))
		self.assertTrue(u2.notifications["repos"]["allowed"])
		self.assertTrue(u2.notifications["repos"]["enabled"])
		# should not have notification for non-existing repository
		self.assertFalse(u2.notifications.has_key("non-existing"))

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
		self.assertTrue(u2.notifications.has_key("repos"))
		self.assertTrue(u2.notifications["repos"]["allowed"])
		self.assertTrue(u2.notifications["repos"]["enabled"])

