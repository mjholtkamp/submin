import os
import unittest
import tempfile
from mock import *

mock_settings = Mock()
mock_settings.storage = "sql"
mock_settings.sqlite_path = ":memory:"
mock_settings.base_dir = "/submin"

from submin.bootstrap import setSettings
setSettings(mock_settings)

from submin.models import storage
from submin.models import options
from submin.models import trac

class TracTests(unittest.TestCase):
	def setUp(self):
		self.submin_env = tempfile.mkdtemp(prefix='submin-unittest')
		self.conf_dir = os.path.join(self.submin_env, 'conf')
		os.mkdir(self.conf_dir)
		mock_settings.base_dir = self.submin_env
		storage.open(mock_settings)
		storage.database_evolve()

		options.set_value('vcs_plugins', 'svn')
		options.set_value('svn_dir', 'svn')
		options.set_value('trac_dir', 'trac')
		options.set_value('svn_authz_file', 'conf/authz')
		options.set_value('enabled_trac', 'yes')

		self.svn_dir = str(options.env_path('svn_dir'))
		self.trac_dir = str(options.env_path('trac_dir'))
		os.mkdir(self.svn_dir)
		os.mkdir(self.trac_dir)

	def tearDown(self):
		storage.close()
		os.system("rm -rf '%s'" % self.submin_env)

	def testExits(self):
		# Assumes trac-admin is actually installed, but since the rest of
		# the tests need trac-admin, this is not a big problem IMHO.
		# -- Michiel
		self.assertEquals(trac.tracAdminExists(), True)

	def testNotExits(self):
		oldpath = os.environ['PATH']
		del os.environ['PATH']
		exists = trac.tracAdminExists()
		os.environ['PATH'] = oldpath
		self.assertEquals(exists, True)

	def testTracCreate(self):
		mock_admin = Mock()
		mock_admin.is_admin = True
		mock_admin.name = "admin"
		trac.createTracEnv("test", mock_admin)

if __name__ == "__main__":
	unittest.main()
