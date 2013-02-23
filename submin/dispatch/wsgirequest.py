import os
import sys
from submin.models import options

from request import Request, CGIGet, CGIFieldStorage

class WSGIRequest(Request):
	def __init__(self, environ):
		Request.__init__(self)
		self.__environ = environ

		if 'REQUEST_URI' in environ:
			self.url = environ['REQUEST_URI']
		else:
			self.url = environ['PATH_INFO']

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

		# When running from stand-alone WSGI-server, we have no Alias.
		# Instead, we can define part of the URL to be cut so we can
		# use e.g. /submin/ in front of the URL.
		if 'SUBMIN_REMOVE_BASE_URL' in environ:
			self.remove_base_url = True
			alias = options.value('base_url_submin')
			if self.path_info.startswith(alias):
				self.path_info = self.path_info[len(alias):]

		self.remote_address = self.__environ.get('REMOTE_ADDR')
		self.https = self.__environ.get('HTTPS', 'off') == 'on'
		self.http_host = self.__environ.get('HTTP_HOST')
