import os
import sys
import cgi

from request import Request, GetVariables

class CGIRequest(Request):
	def __init__(self):
		Request.__init__();
		self.__environ = os.environ
		self.__input = sys.stdin
		self.__output = sys.stdout
		
		self.post = {}
		self.get = CGIGet(self.__environ.get('QUERY_STRING'))
		self.__incookie.load(self.__environ.get('HTTP_COOKIE', '')) 
		self.path_info = self.__environ.get('PATH_INFO', '')
		self.remote_address = self.__environ.get('REMOTE_ADDR')
	
	def write(self, content):
		self.__output.write(content)

class CGIGet(GetVariables):
	def __init__(self, query_string):
		self.variables = cgi.parse_qs(query_string)