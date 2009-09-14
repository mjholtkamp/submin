#!/usr/bin/python
import os
import sys

class application:
	def __init__(self, environ, start_response):
		self.environ = environ
		self.start = start_response
		if not environ.has_key('SUBMIN_ENV'):
			start_response('200 ok', [])
			return 'Please set SUBMIN_ENV in your apache config (ie. via SetEnv)'
		os.environ['SUBMIN_ENV'] = self.environ['SUBMIN_ENV']

		# __file__ contains <submin-dir>/www/submin.wsgi
		submindir = os.path.dirname(os.path.dirname(__file__))
		sys.path.append(os.path.join(submindir, 'lib'))
		from models import backend

		backend.open()

	def __del__(self):
		backend.close()

	def __iter__(self):
		try:
			from dispatch.wsgirequest import WSGIRequest
			from dispatch import dispatcher

			req = WSGIRequest(self.environ)
			response = dispatcher(req)
			self.start(response.status(), response.headers.items())
			for line in response.content.encode('utf-8'):
				yield line
		except Exception, e:
			import traceback
			trace = traceback.extract_tb(sys.exc_info()[2])
			list = traceback.format_list(trace)
			list.append(str(e))
			self.start('500 Not Ok', [])
			yield ''.join(list)

