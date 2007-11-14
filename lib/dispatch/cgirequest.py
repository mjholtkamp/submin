import os
import sys
import cgi

from request import Request, GetVariables

class CGIRequest(Request):
	def __init__(self):
		Request.__init__(self)
		self.__environ = os.environ
		self.__input = sys.stdin
		self.__output = sys.stdout
		
		self.post = CGIFieldStorage(self.__input, environ=self.__environ,
			keep_blank_values=1)
		self.get = CGIGet(self.__environ.get('QUERY_STRING'))
		if self.__environ.get('HTTP_COOKIE'):
			self._incookies.load(self.__environ.get('HTTP_COOKIE', '')) 
		self.path_info = self.__environ.get('PATH_INFO', '')
		self.remote_address = self.__environ.get('REMOTE_ADDR')
	
	def write(self, content):
		self.__output.write(content)
		self.__output.flush()

class CGIGet(GetVariables):
	def __init__(self, query_string):
		self.variables = {}

		if query_string:
			self.variables = cgi.parse_qs(query_string)

class CGIFieldStorage(cgi.FieldStorage):
	"""Provide a consistent way to access the POST variables."""
	
	get = cgi.FieldStorage.getvalue

	def __setitem__(self, name, value):
		if self.has_key(name):
			del self[name]
		self.list.append(cgi.MiniFieldStorage(name, value))

	def __delitem__(self, name):
		if not self.has_key(name):
			raise KeyError(name)
		self.list = filter(lambda x, name=name: x.name != name, self.list)
