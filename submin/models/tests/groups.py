import unittest
from mock import Mock

mock_settings = Mock()
mock_settings.storage = "mock"

from submin.bootstrap import setSettings
setSettings(mock_settings)

from submin.models import group
from submin.models import options
from submin.models import storage
from submin.path.path import Path
from submin.models.exceptions import GroupExistsError, UnknownGroupError

import tempfile
import shutil
import os

class GroupTests(unittest.TestCase):
	def setUp(self):
		self.submin_env = Path(tempfile.mkdtemp(prefix='submin-unittest'))
		conf_dir = self.submin_env + 'conf'
		os.mkdir(conf_dir)
		mock_settings.base_dir = self.submin_env
		storage.open(mock_settings)
		options.set_value('svn_authz_file', conf_dir + 'authz') # needed for export
		options.set_value('svn_dir', self.submin_env + 'svn') # needed for export
		options.set_value('git_dir', self.submin_env + 'git')
		options.set_value('vcs_plugins', 'svn, git')

	def tearDown(self):
		storage.close()
		shutil.rmtree(self.submin_env)

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
		user.add("testUser", email="a@a.a", password="x")
		group.add("testGroup")
		u = user.User("testUser")
		g = group.Group("testGroup")

		g.add_member(u)
		self.assert_("testUser" in g.members())

	def testRemoveMember(self):
		from submin.models import user
		user.add("testUser1", email="a@a.a", password="x")
		user.add("testUser2", email="a@a.a", password="x")
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

if __name__ == "__main__":
	unittest.main()
