import unittest
from config import Config, ConfigData, MissingConfigData, CouldNotReadConfig
import os
import tempfile

class SingletonTest(unittest.TestCase):
	"""Only tests the 'singletonness' of the Config module"""
	def setUp(self):
		self.base = tempfile.mkdtemp()
		self.authz_file = "%s/conf/svn.authz" % self.base
		self.access_file = "%s/conf/htpasswd" % self.base
		self.userprop_file = "%s/conf/userproperties.ini" % self.base
		self.repositories = "%s/svn/" % self.base

		conf_data = """[svn]
authz_file = %s
access_file = %s
userprop_file = %s
repositories = %s

[www]
base_url = /

[generated]
session_salt = 1984500a.cjctec.8""" % \
			(self.authz_file, self.access_file, self.userprop_file, self.repositories)
		
		self.filename = os.path.join(self.base, 'submin.conf')
		fp = open(self.filename, 'w')
		fp.write(conf_data)
		fp.close()
		os.environ['SUBMIN_CONF'] = self.filename
		self.createFiles()

	def createFile(self, filename, content):
		os.system('mkdir -p %s' % os.path.dirname(filename))
		fp = open(filename, 'w+').write(content)

	def createFiles(self):
		authz_content = ""
		access_content = "admin:$1$9BEYXPLN$UtPfDFp1XmyXO0NuMStTP."
		userprop_content = ""

		self.createFile(self.authz_file, authz_content)
		self.createFile(self.access_file, access_content)
		self.createFile(self.userprop_file, userprop_content)

	def tearDown(self):
		os.system("rm -rf '%s'" % self.base)

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

class IncompleteConfigTest(unittest.TestCase):
	def setUp(self):
		self.base = tempfile.mkdtemp()

	def tearDown(self):
		os.system("rm -rf '%s'" % self.base)

	def writeConfig(self, conf_data):
		self.filename = os.path.join(self.base, 'submin.conf')
		fp = open(self.filename, 'w')
		fp.write(conf_data)
		fp.close()
		os.environ['SUBMIN_CONF'] = self.filename

	def testNoConfig(self):
		os.environ['SUBMIN_CONF'] = '/tmp/non-existing.file'
		self.assertRaises(CouldNotReadConfig, Config)

	def testNoSvnSection(self):
		self.writeConfig("")
		self.assertRaises(MissingConfigData, Config)

	def testNoAuthzOption(self):
		self.writeConfig("[svn]")
		self.assertRaises(MissingConfigData, Config)

	def testNoUserPropOption(self):
		self.writeConfig("[svn]\nauthz_file=%s/submin-unittest-authz" % self.base)
		self.assertRaises(MissingConfigData, Config)

	def testNoAccessFileOption(self):
		self.writeConfig("""
[svn]
authz_file=%(base)s/submin-unittest-authz
userprop_file=%(base)s/submin-unittest-userprop
""" % {'base': self.base})
		self.assertRaises(MissingConfigData, Config)

	def testNoWWWSection(self):
		self.writeConfig("""
[svn]
authz_file=%(base)s/submin-unittest-authz
userprop_file=%(base)s/submin-unittest-userprop
access_file=%(base)s/submin-unittest-access-file
""" % {'base': self.base})
		self.assertRaises(MissingConfigData, Config)

if __name__ == "__main__":
	unittest.main()
