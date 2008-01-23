import unittest
import os
import tempfile
import time

from authz import *

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
		self.assert_(os.path.exists(self.filename),
				'File %s does not exist' % self.filename)

	def testCreateGroupsSection(self):
		# XXX: This actually tests several functions!
		# This test alone does an extra operation authz.save(), therefore we
		# also need a strict save() test!
		self.authz.save()
		lines = open(self.filename).readlines()
		self.assert_('[groups]\n' in lines, '[groups] section not created')

class SaveTest(unittest.TestCase):
	"Testcase for the save() method on the Authz-objects."

	def testModificationTime(self):
		tempdir = tempfile.gettempdir()
		filename = os.path.join(tempdir, 'authz')
		authz = Authz(filename)
		begin = os.path.getmtime(filename)

		print '\nTesting modification time. This takes at least 1.1 seconds'
		# sleep required to up the modification-time, reported in seconds
		time.sleep(1.1)
		authz.save()
		end = os.path.getmtime(filename)
		self.assert_(end > begin, 'Modification time after save not past ' \
				+ 'modification time before save (begin > end)')

if __name__ == '__main__':
	unittest.main()
