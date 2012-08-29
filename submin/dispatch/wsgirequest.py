import os
import sys

from request import Request, CGIGet, CGIFieldStorage

class WSGIRequest(Request):
	def __init__(self, environ):
		Request.__init__(self)
		self.__environ = environ

		self.url = environ['REQUEST_URI']
		self.method = environ['REQUEST_METHOD']
		input = environ['wsgi.input']
		self.post = CGIFieldStorage(input, environ=environ, keep_blank_values=1)
		self.get = CGIGet(self.__environ['QUERY_STRING'])

		# Mimic CGI behaviour
		for key, value in self.get.variables.iteritems():
			self.post[key] = value

		if self.__environ.get('HTTP_COOKIE'):
			self._incookies.load(self.__environ.get('HTTP_COOKIE', ''))
		self.path_info = unicode(self.__environ.get('PATH_INFO', ''), 'utf-8')
		self.remote_address = self.__environ.get('REMOTE_ADDR')
		self.https = self.__environ.get('HTTPS', 'off') == 'on'
		self.http_host = self.__environ.get('HTTP_HOST')
