import unittest
from pmock import *

mock_settings = Mock()
mock_settings.storage = "mock"
mock_settings.base_dir = "/submin"

from submin.models import storage
from submin.models.options import Options

class OptionTests(unittest.TestCase):
	def setUp(self):
		storage.open(mock_settings)
		self.o = Options()

	def tearDown(self):
		storage.close()

	def testNoOptions(self):
		self.assertEquals(self.o.options(), {})

	def testSetOption(self):
		self.o.set_value("foo", "bar")
		self.assertEquals(self.o.options(), {"foo": "bar"})

	def testGetOption(self):
		self.o.set_value("foo", "bar")
		self.assertEquals(self.o.value("foo"), "bar")

	def testPath(self):
		self.o.set_value("foo", "bar")
		self.assertEquals(unicode(self.o.env_path("foo")), "/submin/bar")

	def testAbsolutePath(self):
		self.o.set_value("foo", "/bar")
		self.assertEquals(unicode(self.o.env_path("foo")), "/bar")
