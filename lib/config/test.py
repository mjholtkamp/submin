import unittest
from config import Config, ConfigData
import os
import tempfile

conf_data = """[svn]
authz_file = /var/www/ilaro.nl/dev/submin/conf/svn.authz
access_file = /var/www/ilaro.nl/dev/submin/conf/.htpasswd
userprop_file = /var/www/ilaro.nl/dev/submin/conf/userproperties.ini
repositories = /var/lib/submin/svn/

[www]
media_url = /

[generated]
session_salt = 1984500a.cjctec.8"""

class SingletonTest(unittest.TestCase):
	"""Only tests the 'singletonness' of the Config module"""
	def setUp(self):
		tempdir = tempfile.gettempdir()
		self.filename = os.path.join(tempdir, 'submin.conf')
		fp = open(self.filename, 'a+')
		fp.write(conf_data)
		fp.close()
		os.environ['SUBMIN_CONF'] = self.filename

	def tearDown(self):
		os.unlink(self.filename)

	def testInstanceEqual(self):
		config_instance = Config()
		self.assert_(config_instance._configdata_instance is Config.instance)

	def testInstanceNotEqualToNew(self):
		config_instance = Config()
		config_data_instance = ConfigData()
		self.assert_(config_instance._configdata_instance \
				is not config_data_instance)

	def testSharedInstance(self):
		c1 = Config()
		c2 = Config()
		self.assert_(c1._configdata_instance is c2._configdata_instance)

	def testGetAttribute(self):
		config_instance = Config()
		self.assert_(config_instance.authz)

if __name__ == "__main__":
	unittest.main()
