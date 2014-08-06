import unittest

from mock import Mock

mock_settings = Mock()
mock_settings.storage = "sql"
mock_settings.sqlite_path = ":memory:"
mock_settings.base_dir = "/"

from submin.bootstrap import setSettings
setSettings(mock_settings)

from submin.models import storage
from submin.models import options
from .decorators import generate_acl_list

class GenerateACLTests(unittest.TestCase):
	def setUp(self):
		storage.open(mock_settings)
		storage.database_evolve()

	def tearDown(self):
		storage.close()

	def testCompleteVhost(self):
		options.set_value('http_vhost', 'http://example.net/')
		self.assertGreater(len(generate_acl_list()), 2)

	def testVhostWithoutScheme(self):
		options.set_value('http_vhost', 'example.net')
		self.assertGreater(len(generate_acl_list()), 2)

	def testCompleteVhostIPv6(self):
		options.set_value('http_vhost', 'http://[2001:db8::1]/')
		self.assertGreater(len(generate_acl_list()), 2)

	def testVhostWithoutSchemeIPv6(self):
		options.set_value('http_vhost', '[2001:db8::1]')
		self.assertGreater(len(generate_acl_list()), 2)

	def testCompleteVhostWithPort(self):
		options.set_value('http_vhost', 'http://example.net:80/')
		self.assertGreater(len(generate_acl_list()), 2)

	def testVhostWithoutSchemeWithPort(self):
		options.set_value('http_vhost', 'example.net:80')
		self.assertGreater(len(generate_acl_list()), 2)

	def testCompleteVhostIPv6WithPort(self):
		options.set_value('http_vhost', 'http://[2001:db8::1]:80/')
		self.assertGreater(len(generate_acl_list()), 2)

	def testVhostWithoutSchemeIPv6WithPort(self):
		options.set_value('http_vhost', '[2001:db8::1]:80')
		self.assertGreater(len(generate_acl_list()), 2)

	def testNonsense(self):
		options.set_value('http_vhost', ':80')
		self.assertEquals(len(generate_acl_list()), 2)


if __name__ == "__main__":
	unittest.main()
