import unittest
from pmock import *

mock_settings = Mock()
mock_settings.storage = "mock"
mock_settings.base_dir = "/tmp/submin"

from submin.models import storage
from submin.models import group
from submin.models import options
from submin.models.exceptions import GroupExistsError, UnknownGroupError

class GroupTests(unittest.TestCase):
	def setUp(self):
		storage.open(mock_settings)
		options.set_value('svn_authz_file', '/tmp/submin-authz') # needed for export
		options.set_value('svn_dir', '/tmp/submin-svn') # needed for export
		options.set_value('vcs_plugins', 'svn')

	def tearDown(self):
		import os
		storage.close()
		try:
			os.unlink('/tmp/submin-authz')
		except OSError:
			pass

	def testEmptyList(self):
		fake_admin = Mock()
		fake_admin.is_admin = True
		self.assertEquals(group.list(fake_admin), [])

	def testNonEmptyList(self):
		group.add("test")
		fake_admin = Mock()
		fake_admin.is_admin = True
		self.assertEquals([g for g in group.list(fake_admin)], ["test"])

	def testGetGroup(self):
		group.add("foo")
		g = group.Group("foo")
		self.assertEquals(g.name, "foo")

	def testUnknownGroup(self):
		self.assertRaises(UnknownGroupError, group.Group, "nonexisting")

	def testAddDoubleGroup(self):
		group.add("test")
		self.assertRaises(GroupExistsError, group.add, "test")

	def testRemoveGroup(self):
		group.add("foo")
		foo = group.Group("foo")
		fake_admin = Mock()
		fake_admin.is_admin = True
		foo.remove()
		self.assert_("foo" not in [x.name for x in group.list(fake_admin)])

	def testEmptyMemberList(self):
		group.add("foo")
		foo = group.Group("foo")
		self.assertEquals(foo.members(), [])

	def testAddMember(self):
		from submin.models import user
		user.add("testUser")
		group.add("testGroup")
		u = user.User("testUser")
		g = group.Group("testGroup")

		g.add_member(u)
		self.assert_("testUser" in g.members())

	def testRemoveMember(self):
		from submin.models import user
		user.add("testUser1")
		user.add("testUser2")
		group.add("testGroup")
		u1 = user.User("testUser1")
		u2 = user.User("testUser2")
		g = group.Group("testGroup")
		g.add_member(u1)
		g.add_member(u2)
		g.remove_member(u2)
		self.assert_("testUser2" not in g.members())

# TODO: test integration between Group and User
# especially when removing a Group, that group should no longer be available
# via user.member_of()!
