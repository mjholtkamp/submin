import unittest
from config import Config, ConfigData
import os
import tempfile

authz_file = "/tmp/submin-unittest/conf/svn.authz"
access_file = "/tmp/submin-unittest/conf/htpasswd"
userprop_file = "/tmp/submin-unittest/conf/userproperties.ini"
repositories = "/tmp/submin-unittest/svn/"

conf_data = """[svn]
authz_file = %s
access_file = %s
userprop_file = %s
repositories = %s

[www]
base_url = /

[generated]
session_salt = 1984500a.cjctec.8""" % (authz_file, access_file, userprop_file, repositories)

authz_content = ""
access_content = "admin:$1$9BEYXPLN$UtPfDFp1XmyXO0NuMStTP."
userprop_content = ""

class SingletonTest(unittest.TestCase):
	"""Only tests the 'singletonness' of the Config module"""
	def setUp(self):
		tempdir = tempfile.gettempdir()
		self.filename = os.path.join(tempdir, 'submin.conf')
		fp = open(self.filename, 'a+')
		fp.write(conf_data)
		fp.close()
		os.environ['SUBMIN_CONF'] = self.filename
		self.createFiles()

	def createFile(self, filename, content):
		os.system('mkdir -p %s' % os.path.dirname(filename))
		fp = open(filename, 'w+')
		fp.write(content)
		fp.close

	def createFiles(self):
		self.createFile(authz_file, authz_content)
		self.createFile(access_file, access_content)
		self.createFile(userprop_file, userprop_content)

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
