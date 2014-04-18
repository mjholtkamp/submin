import sys
import unittest
import c_quit
import c_config
import c_help
import os
import tempfile
import shutil # to remove temp dir
from mock import Mock, MagicMock
from StringIO import StringIO

mock_settings = Mock()
mock_settings.storage = "sql"
mock_settings.sqlite_path = ":memory:"
mock_settings.base_dir = "/"

from submin.bootstrap import setSettings
setSettings(mock_settings)

from submin.path.path import Path
from submin.models import storage
from submin.models import options
from submin.models.exceptions import UnknownKeyError

class SubminAdminApacheConfTests(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.tmpdir = tempfile.mkdtemp(prefix='submin-unittest')
		conf_dir = os.path.join(cls.tmpdir, 'conf')
		os.mkdir(conf_dir)
		file(os.path.join(conf_dir, 'settings.py'), 'w').writelines(
		"""import os
storage = "sql"
sqlite_path = os.path.join(os.path.dirname(__file__), "submin.db")
"""
		)
		os.environ['SUBMIN_ENV'] = cls.tmpdir

	@classmethod
	def tearDownClass(cls):
		os.system("rm -rf '%s'" % cls.tmpdir)

	def testUrlPathEmpty(self):
		import c_apacheconf
		ac = c_apacheconf.c_apacheconf(None, [])
		result = ac.urlpath('')
		self.assertEquals(result, '/')

	def testUrlPathSlash(self):
		import c_apacheconf
		ac = c_apacheconf.c_apacheconf(None, [])
		result = ac.urlpath('/')
		self.assertEquals(result, '/')

	def testUrlPathFullURL(self):
		import c_apacheconf
		ac = c_apacheconf.c_apacheconf(None, [])
		result = ac.urlpath('http://www.example.com/')
		self.assertEquals(result, '/')

	def testUrlPathFullURLSubDir(self):
		import c_apacheconf
		ac = c_apacheconf.c_apacheconf(None, [])
		result = ac.urlpath('http://www.example.com/submin/help')
		self.assertEquals(result, '/submin/help')

	def testUrlPathURLpath(self):
		import c_apacheconf
		ac = c_apacheconf.c_apacheconf(None, [])
		result = ac.urlpath('/submin/')
		self.assertEquals(result, '/submin')

class SubminAdminQuit(unittest.TestCase):
	def testQuit(self):
		env = Mock()
		env.quit = False
		q = c_quit.c_quit(env, [])
		self.assertRaises(SystemExit, q.run())

class SubminAdminConfig(unittest.TestCase):
	def setUp(self):
		self.submin_env = Path(tempfile.mkdtemp(prefix='submin-unittest'))
		conf_dir = self.submin_env + 'conf'
		os.mkdir(conf_dir)
		mock_settings.base_dir = self.submin_env
		storage.open(mock_settings)
		storage.database_evolve()
		self.sa = MagicMock()
		self.sa.env = self.submin_env
		self.saved_stdout, sys.stdout = sys.stdout, StringIO()

	def tearDown(self):
		storage.close()
		shutil.rmtree(self.submin_env)
		sys.stdout = self.saved_stdout

	def testSetOption(self):
		c = c_config.c_config(self.sa, ['set', 'answer', '42'])
		c.run()
		self.assertEquals(options.value('answer'), u'42')

	def testGetOption(self):
		options.set_value('answer', '42')
		c = c_config.c_config(self.sa, ['get', 'answer'])
		c.run()
		self.assertTrue('42' in sys.stdout.getvalue())

	def testGetUnknownOption(self):
		c = c_config.c_config(self.sa, ['get', 'answer'])
		c.run()
		self.assertEquals('ERROR: answer does not exist\n', sys.stdout.getvalue())

	def testGetAllOptions(self):
		options.set_value('answer', '42')
		c = c_config.c_config(self.sa, ['get'])
		c.run()
		output = sys.stdout.getvalue()
		self.assertTrue('database_version' in output)
		self.assertTrue('git_dir' in output)
		self.assertTrue('42' in output)

	def testDefaults(self):
		expected = [(u'database_version', u'10'), (u'auth_type', u'sql'),
				(u'svn_dir', u'svn'), (u'git_dir', u'git'),
				(u'env_path', u'/bin:/usr/bin:/usr/local/bin:/opt/local/bin'),
				(u'dir_bin', u'static/bin'),(u'base_url_trac', u'/trac'),
				(u'base_url_git', u'/git'), (u'base_url_submin', u'/submin'),
				(u'http_vhost', u'darim'), (u'enabled_trac', u'no'),
				(u'trac_dir', u'trac'), (u'vcs_plugins', u'svn'),
				(u'base_url_svn', u'/svn')]
		unpredictable_keys = [u'session_salt']
		c = c_config.c_config(self.sa, ['defaults'])
		c.run()

		observed = options.options()
		for idx, opt in enumerate(observed):
			key, value = opt
			if key in unpredictable_keys:
				del observed[idx]

		self.assertEquals(expected, observed)

	def testUnsetOption(self):
		options.set_value('answer', '42')
		c = c_config.c_config(self.sa, ['unset', 'answer'])
		c.run()
		self.assertRaises(UnknownKeyError, options.value, 'answer')

class SubminAdminHelp(unittest.TestCase):
	def _cmd_instance(self, string, array, print_error=False):
		instance = Mock()
		instance.__doc__ = 'short mock description\nlong mock description'
		return instance

	def setUp(self):
		self.sa = MagicMock()
		self.sa.cmd_alias.return_value = 'mock'
		self.sa.cmd_instance = self._cmd_instance
		self.sa.commands.return_value = ['mock']
		self.saved_stdout, sys.stdout = sys.stdout, StringIO()

	def tearDown(self):
		sys.stdout = self.saved_stdout

	def testHelpNone(self):
		h = c_help.c_help(self.sa, [])
		h.run()
		self.assertTrue('short mock description' in sys.stdout.getvalue())

	def testHelpSome(self):
		h = c_help.c_help(self.sa, ['mock'])
		h.run()
		self.assertTrue('long mock description' in sys.stdout.getvalue())

	def testHelpUnknown(self):
		self.sa.cmd_instance = Mock(return_value=None)
		h = c_help.c_help(self.sa, ['mock'])
		h.run()
		self.assertTrue('No help available' in sys.stdout.getvalue())

	def testHelpImportError(self):
		self.sa.cmd_instance = Mock(return_value=None)
		h = c_help.c_help(self.sa, [])
		h.run()
		self.assertTrue('module import failed' in sys.stdout.getvalue())

	def testHelpMissingDoc(self):
		instance = Mock()
		instance.__doc__ = None
		self.sa.cmd_instance = Mock(return_value=instance) # without __doc__
		h = c_help.c_help(self.sa, [])
		h.run()
		self.assertTrue('No help available' in sys.stdout.getvalue())

	def testHelpSubminAdmin(self):
		"""WARNING: This test will fail if options is imported prematurely.
		If this test fails, this is problably because options is imported prematurely
		This is a restriction in subminadmin, because you need to be able to run 'help'
		without having an environment (like we do in this test) and the 'options' module
		needs a working environment. In the case that options is imported prematurely,
		import it later (inside a function, but not in __init__)"""
		from subminadmin import SubminAdmin
		sa = SubminAdmin(['submin2-admin', '/tmp/nothing', '?'])
		sa.run()
		self.assertTrue('to get more information on that command' in sys.stdout.getvalue())

if __name__ == "__main__":
	unittest.main()
