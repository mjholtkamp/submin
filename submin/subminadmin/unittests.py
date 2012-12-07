import sys
import unittest
import c_apacheconf
import c_quit
import c_help
from mock import Mock, MagicMock
from StringIO import StringIO

class SubminAdminApacheConfTests(unittest.TestCase):
	def testUrlPathEmpty(self):
		ac = c_apacheconf.c_apacheconf(None, [])
		result = ac.urlpath('')
		self.assertEquals(result, '/')

	def testUrlPathSlash(self):
		ac = c_apacheconf.c_apacheconf(None, [])
		result = ac.urlpath('/')
		self.assertEquals(result, '/')

	def testUrlPathFullURL(self):
		ac = c_apacheconf.c_apacheconf(None, [])
		result = ac.urlpath('http://www.example.com/')
		self.assertEquals(result, '/')

	def testUrlPathFullURLSubDir(self):
		ac = c_apacheconf.c_apacheconf(None, [])
		result = ac.urlpath('http://www.example.com/submin/help')
		self.assertEquals(result, '/submin/help')

	def testUrlPathURLpath(self):
		ac = c_apacheconf.c_apacheconf(None, [])
		result = ac.urlpath('/submin/')
		self.assertEquals(result, '/submin')

class SubminAdminQuit(unittest.TestCase):
	def testQuit(self):
		env = Mock()
		env.quit = False
		q = c_quit.c_quit(env, [])
		self.assertRaises(SystemExit, q.run())

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
		"""WARNING: This test will fail is options is imported prematurely.
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
