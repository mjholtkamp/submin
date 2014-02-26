import os
import sys

from request import Request, CGIGet, CGIFieldStorage

class CGIRequest(Request):
	def __init__(self):
		Request.__init__(self)
		self.__environ = os.environ
		self.__input = sys.stdin
		self.__output = sys.stdout

		self.url = os.environ.get('REQUEST_URI', '')
		
		self.post = CGIFieldStorage(self.__input, environ=self.__environ,
			keep_blank_values=1)
		self.get = CGIGet(self.__environ.get('QUERY_STRING'))
		if self.__environ.get('HTTP_COOKIE'):
			self._incookies.load(self.__environ.get('HTTP_COOKIE', '')) 
		self.path_info = unicode(self.__environ.get('PATH_INFO', ''), 'utf-8')
		self.remote_address = self.__environ.get('REMOTE_ADDR')
	
	def write(self, content):
		self.__output.write(content.encode('utf-8'))
		self.__output.flush()
