import os
import sys
import unittest
from mock import Mock

mock_settings = Mock()
mock_settings.storage = "mock"

from submin.bootstrap import setSettings
setSettings(mock_settings)

from submin.models import repository
from submin.models import options
from submin.models import storage

model_tests = ["users.UserTests", "groups.GroupTests", "options.OptionTests"]

def suite():
	s = unittest.TestSuite()
	subtests = ["submin.models.tests.%s" % x for x in model_tests]
	subtests.append("submin.models.unittests.RepositoryTests")
	map(s.addTest, map(unittest.defaultTestLoader.loadTestsFromName, subtests))
	return s

class RepositoryTests(unittest.TestCase):
	def setUp(self):
		import tempfile
		self.submin_env = tempfile.mkdtemp(prefix='submin-unittest')
		self.conf_dir = os.path.join(self.submin_env, 'conf')
		os.mkdir(self.conf_dir)
		self.authz_file = os.path.join(self.submin_env, 'conf', 'authz')

		mock_settings.base_dir = self.submin_env
		storage.open(mock_settings)
		options.set_value('vcs_plugins', 'svn')
		options.set_value('svn_dir', 'svn')
		options.set_value('trac_dir', 'trac')
		options.set_value('svn_authz_file', 'conf/authz')
		options.set_value('enabled_trac', 'no')

		self.svn_dir = str(options.env_path('svn_dir'))
		self.trac_dir = str(options.env_path('trac_dir'))
		os.mkdir(self.svn_dir)
		os.mkdir(self.trac_dir)

		# now make some repositories
		self.repositories = [
			{'name': 'foo', 'status': 'ok', 'vcs': 'svn'},
			{'name': 'invalidperm', 'status': 'permission denied', 'vcs': 'svn'},
			{'name': 'invalidperm2', 'status': 'permission denied', 'vcs': 'svn'},
			{'name': 'subdirs', 'status': 'ok', 'vcs': 'svn'},
		]
		for r in self.repositories:
			os.system("svnadmin create '%s'" % os.path.join(self.svn_dir, r['name']))

		os.system("chmod 000 '%s'" % \
			os.path.join(self.svn_dir, 'invalidperm'))

		os.system("chmod 000 '%s'" % \
			os.path.join(self.svn_dir, 'invalidperm2', 'db', 'revs'))

	def tearDown(self):
		storage.close()
		os.system("chmod 777 '%s'" % os.path.join(self.svn_dir, 'invalidperm'))
		os.system("chmod 777 '%s'" % \
			os.path.join(self.svn_dir, 'invalidperm2', 'db', 'revs'))
		os.system("rm -rf '%s'" % self.submin_env)

	def testRepositoriesOnDisk(self):
		result = repository.Repository.list_all()
		result.sort()
		copy = self.repositories[:]
		copy.sort()
		self.assertEquals(result, copy)

	def testListRepositoriesAll(self):
		"""Test listRepositories, which checks for valid permissions of repositories"""
		self.assertEquals("", "This test fails because list is not filtering correctly")
		mock_user = Mock()
		mock_user.is_admin = False

		result = repository.Repository.list(mock_user)
		copy = self.repositories[:]
		copy = [d for d in self.repositories if d.get('name') == 'foo' or d.get('name') == 'subdirs']
		copy.sort()
		self.assertEquals(result, copy)

	def testExistingRepository(self):
		r = repository.Repository('foo', 'svn')
		self.assertEquals(r.name, 'foo')

	def testInvalidPermRepository(self):
		self.assertRaises(repository.PermissionError, repository.Repository, "invalidperm", "svn")

	def testInvalidPermRepository2(self):
		self.assertRaises(repository.PermissionError, repository.Repository, "invalidperm2", "svn")

	def testUnknownRepository(self):
		self.assertRaises(repository.DoesNotExistError, repository.Repository, "non-existing-repository", "svn")

	def testHasSubDirs(self):
		for subdir in ['test', 'test/subdir']:
			os.system("svn mkdir -m '' file://'%s' >/dev/null" % \
				os.path.join(self.svn_dir, 'subdirs', subdir))
		r = repository.Repository('subdirs', 'svn')
		subdirs = r.subdirs('test')
		expected = [{'has_subdirs': False, 'name': u'subdir'}]
		self.assertEquals(subdirs, expected)

	def testSubDirsContents(self):
		for subdir in ['test', 'test/subdir', 'nosubdirs']:
			os.system("svn mkdir -m '' file://'%s' >/dev/null" % \
				os.path.join(self.svn_dir, 'subdirs', subdir))
		r = repository.Repository('subdirs', 'svn')
		result = r.subdirs('')
		expected_result = [{'has_subdirs': False, 'name': u'nosubdirs'}, \
			{'name': u'test', 'has_subdirs': True}]

		result.sort()
		expected_result.sort()
		self.assertEquals(result, expected_result)

	def testRemoveRepository(self):
		r = repository.Repository('subdirs', 'svn')
		r.remove()
		self.assertRaises(repository.DoesNotExistError, repository.Repository, 'subdirs', 'svn')

	def testChangeNotificationsEmptyHook(self):
		expected_hook = '''#!/bin/sh
### SUBMIN AUTOCONFIG, DO NOT ALTER FOLLOWING LINE ###
/usr/bin/python /bin/post-commit.py "%s" "$1" "$2"
''' % self.submin_env
		hook_fname = os.path.join(self.svn_dir, 'foo', 'hooks', 'post-commit')

		r = repository.Repository('foo', 'svn')
		r.enableCommitEmails(enable=True)
		hook = ''.join(file(hook_fname, 'r').readlines())
		self.assertTrue('### SUBMIN AUTOCONFIG, DO NOT ALTER FOLLOWING LINE ###' in hook)
		self.assertTrue('mailer.py.conf' in hook)

	def testChangeNotificationsExistingHook(self):
		expected_hook = '''#!/bin/sh
# just a comment
'''
		hook_fname = os.path.join(self.svn_dir, 'foo', 'hooks', 'post-commit')
		file(hook_fname, 'w').write(expected_hook)

		r = repository.Repository('foo', 'svn')
		r.enableCommitEmails(enable=True)
		hook = ''.join(file(hook_fname, 'r').readlines())
		self.assertTrue('# just a comment' in hook)
		self.assertTrue('mailer.py.conf' in hook)
		r.enableCommitEmails(enable=False)
		hook = ''.join(file(hook_fname, 'r').readlines())
		self.assertEquals(hook, expected_hook)

	def testNotificationsEnabled(self):
		r = repository.Repository('foo', 'svn')
		# first time, because no file is present
		self.assertFalse(r.commitEmailsEnabled())
		r.enableCommitEmails(enable=True)
		self.assertTrue(r.commitEmailsEnabled())
		# a second time, because now a file is created
		r.enableCommitEmails(enable=False)
		self.assertFalse(r.commitEmailsEnabled())

if __name__ == "__main__":
	unittest.main()
