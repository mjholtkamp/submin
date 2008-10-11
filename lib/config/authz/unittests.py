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
		self.userpropfilename = os.path.join(tempdir, 'userprops')
		# Easier than using tempfile.mkstemp() because I only need a filename.
		self.authz = Authz(self.filename, self.userpropfilename)

	def tearDown(self):
		os.unlink(self.filename)

	def testCreateFile(self):
		self.assert_(os.path.exists(self.filename),
				'File %s does not exist' % self.filename)

	def testCreateGroupsSection(self):
		self.assert_(self.authz.authzParser.has_section('groups'),
				'[groups] section not created')

class SaveTest(unittest.TestCase):
	"Testcase for the save() method on the Authz-objects."

	def testModificationTime(self):
		tempdir = tempfile.gettempdir()
		filename = os.path.join(tempdir, 'authz')
		userpropfilename = os.path.join(tempdir, 'userprops')
		authz = Authz(filename, userpropfilename)
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
