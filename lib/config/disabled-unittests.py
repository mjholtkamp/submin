import unittest
from config import Config, ConfigData, MissingConfigData, CouldNotReadConfig, NoEnvironment
import os
import tempfile

def ReinitConfig():
	"""In a seperate function, so we can use assertRaises"""
	config = Config() # will raise exceptions the first time
	config.reinit() # will raise exceptions all the other times

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
		if os.environ.has_key('SUBMIN_CONF'):
			del os.environ['SUBMIN_CONF']
		# if os.environ.has_key('SUBMIN_ENV'):
		# 	del os.environ['SUBMIN_ENV']

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
		if os.environ.has_key('SUBMIN_CONF'):
			del os.environ['SUBMIN_CONF']
		if os.environ.has_key('SUBMIN_ENV'):
			del os.environ['SUBMIN_ENV']

	def writeConfig(self, conf_data, base=None, confname='submin.conf'):
		if base == None:
			base = self.base
		try:
			os.makedirs(base)
		except OSError:
			pass
		self.filename = os.path.join(base, confname)
		fp = open(self.filename, 'w')
		fp.write(conf_data)
		fp.close()
		os.environ['SUBMIN_CONF'] = self.filename

	def testNoEnv(self):			
		self.assertRaises(NoEnvironment, ReinitConfig)

	def testEnv2(self):
		os.environ['SUBMIN_ENV'] = self.base
		self.writeConfig("""
[svn]
authz_file=%(base)s/authz
userprop_file=%(base)s/userprop
access_file=%(base)s/access-file

[www]
base_url = /
""" % {'base': self.base}, base=os.path.join(self.base, 'conf'), confname='submin.ini')
		ReinitConfig()
		self.assertEquals(str(Config().base_url), "/")

	def testNoConfig(self):
		os.environ['SUBMIN_CONF'] = '/tmp/non-existing.file'
		self.assertRaises(CouldNotReadConfig, ReinitConfig)

	def testNoSvnSection(self):
		self.writeConfig("")
		self.assertRaises(MissingConfigData, ReinitConfig)

	def testNoAuthzOption(self):
		self.writeConfig("[svn]")
		self.assertRaises(MissingConfigData, ReinitConfig)

	def testNoUserPropOption(self):
		self.writeConfig("[svn]\nauthz_file=%s/submin-unittest-authz" % self.base)
		self.assertRaises(MissingConfigData, ReinitConfig)

	def testNoAccessFileOption(self):
		self.writeConfig("""
[svn]
authz_file=%(base)s/submin-unittest-authz
userprop_file=%(base)s/submin-unittest-userprop
""" % {'base': self.base})
		self.assertRaises(MissingConfigData, ReinitConfig)

	def testNoWWWSection(self):
		self.writeConfig("""
[svn]
authz_file=%(base)s/submin-unittest-authz
userprop_file=%(base)s/submin-unittest-userprop
access_file=%(base)s/submin-unittest-access-file
""" % {'base': self.base})
		self.assertRaises(MissingConfigData, ReinitConfig)

	def testNoBaseUrlOption(self):
		self.writeConfig("""
[svn]
authz_file=%(base)s/submin-unittest-authz
userprop_file=%(base)s/submin-unittest-userprop
access_file=%(base)s/submin-unittest-access-file

[www]
""" % {'base': self.base})
		self.assertRaises(MissingConfigData, ReinitConfig)

if __name__ == "__main__":
	unittest.main()
