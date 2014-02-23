import os
import sys
import unittest
import tempfile
from mock import Mock

mock_settings = Mock()
mock_settings.storage = "sql"
mock_settings.sqlite_path = ":memory:"

from submin.bootstrap import setSettings
setSettings(mock_settings)

from submin.models import repository
from submin.models import user
from submin.models import group
from submin.models import permissions
from submin.models import options
from submin.models import storage

class RepositoryTests(unittest.TestCase):
	def setUp(self):
		self.submin_env = tempfile.mkdtemp(prefix='submin-unittest')
		self.conf_dir = os.path.join(self.submin_env, 'conf')
		os.mkdir(self.conf_dir)
		self.authz_file = os.path.join(self.submin_env, 'conf', 'authz')

		mock_settings.base_dir = self.submin_env
		storage.open(mock_settings)
		storage.database_evolve()
		options.set_value('vcs_plugins', 'svn')
		options.set_value('svn_dir', 'svn')
		options.set_value('trac_dir', 'trac')
		options.set_value('svn_authz_file', 'conf/authz')
		options.set_value('enabled_trac', 'no')
		options.set_value('http_vhost', 'localhost')
		options.set_value('base_url_submin', '/submin')

		self.svn_dir = str(options.env_path('svn_dir'))
		self.trac_dir = str(options.env_path('trac_dir'))
		os.mkdir(self.svn_dir)
		os.mkdir(self.trac_dir)

		# now make some repositories
		self.repositories = [
			{'name': 'foo', 'display_name': 'foo', 'status': 'ok', 'vcs': 'svn'},
			{'name': 'invalidperm', 'display_name': 'invalidperm', 'status': 'permission denied', 'vcs': 'svn'},
			{'name': 'invalidperm2', 'display_name': 'invalidperm2', 'status': 'permission denied', 'vcs': 'svn'},
			{'name': 'example', 'display_name': 'example', 'status': 'ok', 'vcs': 'svn'},
			{'name': 'subdirs', 'display_name': 'subdirs', 'status': 'ok', 'vcs': 'svn'},
		]
		self.has_invalidperm = False
		self.has_invalidperm2 = False

	def _createRepos(self, reponames):
		for repo in filter(lambda x: x['name'] in reponames, self.repositories):
			#[x for x in self.repositories if x['name'] in reponames]:
			os.system("svnadmin create '%s'" % os.path.join(self.svn_dir, repo['name']))
			if repo['name'] == 'invalidperm':
				self.has_invalidperm = True
				os.system("chmod 000 '%s'" % \
					os.path.join(self.svn_dir, 'invalidperm'))

			if repo['name'] == 'invalidperm2':
				self.has_invalidperm2 = True
				os.system("chmod 000 '%s'" % \
					os.path.join(self.svn_dir, 'invalidperm2', 'db', 'revs'))

	def tearDown(self):
		storage.close()
		if self.has_invalidperm:
			os.system("chmod 777 '%s'" % os.path.join(self.svn_dir, 'invalidperm'))
			self.has_invalidperm = False

		if self.has_invalidperm2:
			os.system("chmod 777 '%s'" % \
				os.path.join(self.svn_dir, 'invalidperm2', 'db', 'revs'))
			self.has_invalidperm2

		os.system("rm -rf '%s'" % self.submin_env)

	def testRepositoriesOnDisk(self):
		self._createRepos([x['name'] for x in self.repositories])
		result = repository.Repository.list_all()
		result.sort()
		copy = self.repositories[:]
		copy.sort()
		self.assertEquals(result, copy)

	def testListRepositoriesAll(self):
		"""Test listRepositories, which checks for valid permissions of repositories"""
		self._createRepos([x['name'] for x in self.repositories])
		mock_admin = Mock()
		mock_admin.is_admin = True
		u = user.add('bar', 'a@a.a', send_mail=False)
		g = group.add('baz') # no members in this group
		g = group.add('quux')
		g.add_member(u)
		permissions.add('foo', 'svn', '/', 'bar', 'user', 'r')
		permissions.add('subdirs', 'svn', '/trunk', 'quux', 'group', 'rw')
		# 'bar' is not part of group 'baz', so 'example' should not be listed
		permissions.add('example', 'svn', '/', 'baz', 'group', 'r')

		result = repository.Repository.list(u)
		copy = self.repositories[:]
		copy = [d for d in self.repositories if d.get('name') == 'foo' or d.get('name') == 'subdirs']
		copy.sort()
		self.assertEquals(result, copy)

	def testExistingRepository(self):
		self._createRepos(['foo'])
		r = repository.Repository('foo', 'svn')
		self.assertEquals(r.name, 'foo')

	def testInvalidPermRepository(self):
		self._createRepos(['invalidperm'])
		self.assertRaises(repository.PermissionError, repository.Repository, "invalidperm", "svn")

	def testInvalidPermRepository2(self):
		self._createRepos(['invalidperm2'])
		self.assertRaises(repository.PermissionError, repository.Repository, "invalidperm2", "svn")

	def testUnknownRepository(self):
		self.assertRaises(repository.DoesNotExistError, repository.Repository, "non-existing-repository", "svn")

	def testHasSubDirs(self):
		self._createRepos(['subdirs'])
		for subdir in ['test', 'test/subdir']:
			os.system("svn mkdir -m '' file://'%s' >/dev/null" % \
				os.path.join(self.svn_dir, 'subdirs', subdir))
		r = repository.Repository('subdirs', 'svn')
		subdirs = r.subdirs('test')
		expected = [{'has_subdirs': False, 'name': u'subdir'}]
		self.assertEquals(subdirs, expected)

	def testSubDirsContents(self):
		self._createRepos(['subdirs'])
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
		self._createRepos(['subdirs'])
		r = repository.Repository('subdirs', 'svn')
		r.remove()
		self.assertRaises(repository.DoesNotExistError, repository.Repository, 'subdirs', 'svn')

	def testChangeNotificationsEmptyHook(self):
		self._createRepos(['foo'])
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
		self._createRepos(['foo'])
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
		self._createRepos(['foo'])
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
