import unittest
from pmock import *

mock_settings = Mock()
mock_settings.backend = "mock"

from models import backend
from models.options import Options

class OptionTests(unittest.TestCase):
	def setUp(self):
		backend.open(mock_settings)
		self.o = Options()

	def tearDown(self):
		backend.close()

	def testNoOptions(self):
		self.assertEquals(self.o.options(), {})

	def testSetOption(self):
		self.o.set_value("foo", "bar")
		self.assertEquals(self.o.options(), {"foo": "bar"})

	def testGetOption(self):
		self.o.set_value("foo", "bar")
		self.assertEquals(self.o.value("foo"), "bar")

	def testPath(self):
		import os
		old = None
		if os.environ.has_key("SUBMIN_ENV"):
			old = os.environ["SUBMIN_ENV"]
		os.environ["SUBMIN_ENV"] = "/submin/"
		self.o.set_value("foo", "bar")
		self.assertEquals(unicode(self.o.path("foo")), "/submin/bar")

		if old:
			os.environ["SUBMIN_ENV"] = old
		else:
			del os.environ["SUBMIN_ENV"]

	def testAbsolutePath(self):
		self.o.set_value("foo", "/bar")
		self.assertEquals(unicode(self.o.path("foo")), "/bar")
