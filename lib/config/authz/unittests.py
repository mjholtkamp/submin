import unittest
import os
import tempfile
import time

from authz import *
from htpasswd import *

class InitTest(unittest.TestCase):
	"Tests the initializer for the Authz-module"

	def setUp(self):
		tempdir = tempfile.gettempdir()
		self.filename = os.path.join(tempdir, 'authz')
		self.userpropfilename = os.path.join(tempdir, 'userprops')
		# Easier than using tempfile.mkstemp() because I only need a filename.
		self.authz = Authz(self.filename, self.userpropfilename)

	def tearDown(self):
		os.unlink(self.filename)
		os.unlink(self.userpropfilename)

	def testCreateFile(self):
		self.assert_(os.path.exists(self.filename),
				'File %s does not exist' % self.filename)
		self.assert_(os.path.exists(self.userpropfilename),
				'File %s does not exist' % self.userpropfilename)

	def testCreateGroupsSection(self):
		self.assert_(self.authz.authzParser.has_section('groups'),
				'[groups] section not created')
	
	def testAddGroup(self):
		self.authz.addGroup('foo', ['bar'])
		self.assertEquals(self.authz.members('foo'), ['bar'])
		self.authz.addMember('foo', 'baz')
		self.assertEquals(self.authz.members('foo'), ['bar', 'baz'])

	def testRemoveGroup(self):
		self.authz.addGroup('foo', ['bar', 'baz'])
		self.authz.removeMember('foo', 'baz')
		self.assertEquals(self.authz.members('foo'), ['bar'])
		
	def testDoubleGroupAdd(self):
		self.authz.addGroup('foo', ['bar'])
		self.assertRaises(GroupExistsError, self.authz.addGroup, 'foo')

	def testDoubleMemberAdd(self):
		self.authz.addGroup('foo', ['bar'])
		self.assertRaises(MemberExistsError, self.authz.addMember, 'foo', 'bar')

	def testRemoveUnknownMember(self):
		self.authz.addGroup('foo', ['bar'])
		self.assertRaises(UnknownMemberError, self.authz.removeMember, 'foo', 'baz')

	def testRemoveUnknownGroup(self):
		self.assertRaises(UnknownGroupError, self.authz.removeGroup, 'foo')
		
	def testSetRemovePermission(self):
		self.authz.setPermission('foo', '/', 'bar', 'user', 'rw')
		self.assertEquals(self.authz.permissions('foo', '/'), [{'type': 'user', 'name': 'bar', 'permission': 'rw'}])
		self.authz.removePermission('foo', '/', 'bar', 'user')
		self.assertEquals(self.authz.permissions('foo', '/'), [])

	def testAddPath(self):
		self.authz.addPath('foo', '/')
		self.assertRaises(PathExistsError, self.authz.addPath, 'foo', '/')

	def testRemovePath(self):
		self.authz.addPath('foo', '/')
		self.authz.removePath('foo', '/')
		self.assertEquals(self.authz.paths(), [])

	def testRemoveAllMembers(self):
		self.authz.addGroup('foo', ['bar', 'baz'])
		self.authz.removeAllMembers('foo')
		self.assertEquals(self.authz.members('foo'), [])

	def testRemoveAllMembersUnknownGroup(self):
		self.assertRaises(UnknownGroupError, self.authz.removeAllMembers, 'foo')

	def testListMembersUnknownGroup(self):
		self.assertRaises(UnknownGroupError, self.authz.members, 'foo')

	def testRemovePermissionsUser(self):
		self.authz.setPermission('foo', '/', 'bar', 'user', 'rw')
		self.assertEquals(self.authz.permissions('foo', '/'), [{'type': 'user', 'name': 'bar', 'permission': 'rw'}])
		self.authz.removePermissions('bar', 'user')
		self.assertEquals(self.authz.permissions('foo', '/'), [])

	def testRemovePermissionsGroup(self):
		self.authz.setPermission('foo', '/', 'bar', 'group', 'rw')
		self.assertEquals(self.authz.permissions('foo', '/'), [{'type': 'group', 'name': 'bar', 'permission': 'rw'}])
		self.authz.removePermissions('bar', 'group')
		self.assertEquals(self.authz.permissions('foo', '/'), [])

	def testCreateSectionName(self):
		self.assertRaises(InvalidRepositoryError, self.authz.createSectionName, None, "/foo")

	def testGroupsSelfCheck(self):
		'''Be destructive and see if module checks that'''
		self.authz.authzParser.remove_section('groups')
		self.assertEquals(self.authz.groups(), [])

	def testMemberOf(self):
		self.authz.addGroup('foo', ['bar'])
		self.assertEquals(self.authz.member_of('bar'), ['foo'])


class SaveTest(unittest.TestCase):
	"Testcase for the save() method on the Authz-objects."

	def testModificationTime(self):
		tempdir = tempfile.gettempdir()
		filename = os.path.join(tempdir, 'authz')
		userpropfilename = os.path.join(tempdir, 'userprops')
		authz = Authz(filename, userpropfilename)
		begin = os.path.getmtime(filename)

		# Testing modification time. This takes at least 1.1 seconds.
		# sleep required to up the modification-time, reported in seconds
		time.sleep(1.1)
		authz.save()
		end = os.path.getmtime(filename)
		self.assert_(end > begin, 'Modification time after save not past ' \
				+ 'modification time before save (begin > end)')

class HTPasswdTest(unittest.TestCase):
	"Tester for htpasswd module"
	def setUp(self):
		import tempfile
		self.file = tempfile.NamedTemporaryFile(dir="/tmp/", prefix="submin_htpasswd_")
		self.ht = HTPasswd(self.file.name)

	def tearDown(self):
		# flush otherwise it will try to do it upon deletion and the file will
		# be removed and so this will fail
		self.ht.flush()
		self.file.close()

	def testAdd(self):
		self.ht.add('test', 'test')
		self.assertEquals(self.ht.users(), ['test'])

	def testRemove(self):
		self.ht.add('test', 'test')
		self.ht.remove('test')
		self.assertEquals(self.ht.users(), [])

	def testChange(self):
		self.ht.add('foo', 'bar')
		self.ht.check('foo', 'bar')
		self.ht.change('foo', 'baz')
		self.assertEquals(self.ht.check('foo', 'baz'), True)
		self.assertEquals(self.ht.check('foo', 'bar'), False)

	def testUnknownUser(self):
		self.assertEquals(self.ht.check('foo', 'baz'), False)
		self.assertEquals(self.ht.change('foo', 'bar'), False)
		self.assertEquals(self.ht.remove('foo'), False)

	def testExists(self):
		self.assertEquals(self.ht.exists('test'), False)
		self.ht.add('test', 'test')
		self.assertEquals(self.ht.exists('test'), True)

	def testInvalidMD5(self):
		self.ht = None
		self.file.write("foo:bar")
		self.file.flush()
		self.ht = HTPasswd(self.file.name)
		self.assertRaises(NoMD5PasswordError, self.ht.check, "foo", "bar")

if __name__ == '__main__':
	unittest.main()
