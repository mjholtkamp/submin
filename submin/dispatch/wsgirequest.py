import os
import sys
import cgi # for parse_qs

from request import Request, GetVariables

class WSGIRequest(Request):
	def __init__(self, environ):
		Request.__init__(self)
		self.__environ = environ

		self.url = environ['REQUEST_URI']
		self.method = environ['REQUEST_METHOD']
		input = environ['wsgi.input']
		self.post = WSGIFieldStorage(input, environ=environ, keep_blank_values=1)
		self.get = WSGIGet(self.__environ['QUERY_STRING'])

		# Mimic CGI behaviour
		for key, value in self.get.variables.iteritems():
			self.post[key] = value

		if self.__environ.get('HTTP_COOKIE'):
			self._incookies.load(self.__environ.get('HTTP_COOKIE', ''))
		self.path_info = self.__environ.get('PATH_INFO', '')
		self.remote_address = self.__environ.get('REMOTE_ADDR')
		self.https = self.__environ.get('HTTPS', 'off') == 'on'
		self.http_host = self.__environ.get('HTTP_HOST')

class WSGIGet(GetVariables):
	def __init__(self, query_string):
		self.variables = {}

		if query_string:
			self.variables = cgi.parse_qs(query_string, keep_blank_values=True)

	def __contains__(self, key):
		return key in self.variables

class WSGIFieldStorage(cgi.FieldStorage):
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

