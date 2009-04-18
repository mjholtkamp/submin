# -*- coding: utf-8 -*-

import unittest
from unicode import *

class UnicodeTests(unittest.TestCase):
	uc_encoded = u"元気"
	utf8_encoded = "元気"
	js_encoded = "%u5143%u6C17"
	uc_esc_encoded = '\\u5143\\u6c17'

	def testJavaScriptUnicodeEncoding(self):
		"""Javascript sometimes encodes unicode like %uFFFF, test if that
		is handled correctly."""
		result = url_uc_decode(self.js_encoded)
		self.assertEquals(self.uc_encoded, result)

	def testUnicodeToUnicode(self):
		"""Encoding a unicode object should return the same object"""
		result = uc_str(self.uc_encoded)
		self.assertEquals(result, self.uc_encoded)

	def testStrToUnicode(self):
		result = uc_str(self.utf8_encoded)
		self.assertEquals(result, self.uc_encoded)

	def testObjToUnicode(self):
		class NotAString(object):
			def __str__(self):
				uc_encoded = u"元気"
				return uc_encoded.encode('utf-8')
		nas = NotAString()
		result = uc_str(nas)
		self.assertEquals(result, self.uc_encoded)

	def testFromSvn(self):
		result = uc_from_svn(self.utf8_encoded)
		self.assertEquals(result, self.uc_encoded)

	def testToSvn(self):
		result = uc_to_svn(self.uc_encoded)
		self.assertEquals(result, self.utf8_encoded)

if __name__ == "__main__":
	unittest.main()