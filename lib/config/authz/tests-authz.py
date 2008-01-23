import unittest
import os
import tempfile

from authz import Authz

class InitTest(unittest.TestCase):
	"Tests the initializer for the Authz-module"

	def setUp(self):
		tempdir = tempfile.gettempdir()
		self.filename = os.path.join(tempdir, 'authz')
		# Easier than using tempfile.mkstemp() because I only need a filename.
		self.authz = Authz(self.filename)

	def tearDown(self):
		os.unlink(self.filename)

	def testCreateFile(self):
		self.assert_(os.path.exists(self.filename))

	def testCreateGroupsSection(self):
		# XXX: This actually tests several functions! (namely the init and the
		# save function). Therefore we also need a strict save() test!
		self.authz.save()
		lines = open(self.filename).readlines()
		self.assert_('[groups]\n' in lines)

if __name__ == '__main__':
	unittest.main()
