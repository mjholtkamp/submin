import unittest
from mock import *

mock_settings = Mock()
mock_settings.storage = "mock"
mock_settings.base_dir = "/submin"

from submin.bootstrap import setSettings
setSettings(mock_settings)

from submin.models import storage
from submin.models import options

class OptionTests(unittest.TestCase):
	def setUp(self):
		storage.open(mock_settings)

	def tearDown(self):
		storage.close()

	def testNoOptions(self):
		self.assertEquals(options.options(), {})

	def testSetOption(self):
		options.set_value("foo", "bar")
		self.assertEquals(options.options(), {"foo": "bar"})

	def testGetOption(self):
		options.set_value("foo", "bar")
		self.assertEquals(options.value("foo"), "bar")

	def testPath(self):
		options.set_value("foo", "bar")
		self.assertEquals(unicode(options.env_path("foo")), "/submin/bar")

	def testAbsolutePath(self):
		options.set_value("foo", "/bar")
		self.assertEquals(unicode(options.env_path("foo")), "/bar")

if __name__ == "__main__":
	unittest.main()
