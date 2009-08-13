import unittest
from pmock import *

mock_settings = Mock()
mock_settings.backend = "mock"

from models import backendOpen, backendSetup, backendClose
from models.group import Group, GroupExistsError, UnknownGroupError

class GroupTests(unittest.TestCase):
	def setUp(self):
		backendOpen(mock_settings)

	def tearDown(self):
		backendClose()

	def testEmptyList(self):
		self.assertEquals(Group.list(), [])

	def testNonEmptyList(self):
		Group.add("test")
		self.assertEquals([g.name for g in Group.list()], ["test"])

	def testGetGroup(self):
		Group.add("foo")
		g = Group("foo")
		self.assertEquals(g.name, "foo")

	def testUnknownGroup(self):
		self.assertRaises(UnknownGroupError, Group, "nonexisting")

	def testAddDoubleGroup(self):
		Group.add("test")
		self.assertRaises(GroupExistsError, Group.add, "test")

	def testRemoveGroup(self):
		Group.add("foo")
		foo = Group("foo")
		foo.remove()
		self.assert_("foo" not in [x.name for x in Group.list()])

	def testEmptyMemberList(self):
		Group.add("foo")
		foo = Group("foo")
		self.assertEquals(foo.members(), [])

	def testAddMember(self):
		from models.user import User
		User.add("testUser")
		Group.add("testGroup")
		u = User("testUser")
		g = Group("testGroup")

		g.add_member(u)
		self.assert_("testUser" in g.members())

	def testRemoveMember(self):
		from models.user import User
		User.add("testUser1")
		User.add("testUser2")
		Group.add("testGroup")
		u1 = User("testUser1")
		u2 = User("testUser2")
		g = Group("testGroup")
		g.add_member(u1)
		g.add_member(u2)
		g.remove_member(u2)
		self.assert_("testUser2" not in g.members())

# TODO: test integration between Group and User
# especially when removing a Group, that group should no longer be available
# via user.member_of()!
