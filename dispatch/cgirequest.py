import os
import sys

from request import Request

class CGIRequest(Request):
	def __init__(self):
		Request.__init__();
		self.__environ = os.environ
		self.__input = sys.stdin
		self.__output = sys.stdout
		
		self.post = {}
		self.get = {}
		self.__incookie.load(self.__environ.get('HTTP_COOKIE', '')) 
		self.path_info = self.__environ.get('PATH_INFO', '')
		self.remote_address = self.__environ.get('REMOTE_ADDR')
	
	def writeHeaders(self):
		raise NotImplementedError
	
	def write(self, content):
		self.__output.write(content);