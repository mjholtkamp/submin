#!/usr/bin/python
import sys
import os

class Application:
	def __init__(self, environ, start_response):
		self.environ = environ
		self.start_response = start_response
		from submin.models import storage
		self.storage = storage
		self.storage.open()

		# importing options is only possbile after storage.open()
		from submin.models import options

		submin_www_dir = options.static_path('www')
		os.chdir(submin_www_dir) # same behaviour as CGI script

		from submin.bootstrap import SubminInstallationCheck
		submin_dir = options.lib_path()
		check = SubminInstallationCheck(submin_dir, environ)
		if not check.ok:
			self.start_response("500 Not Ok", [])
			return check.error_page().encode("utf-8")

		os.environ['SUBMIN_ENV'] = environ['SUBMIN_ENV']

		from submin.dispatch.wsgirequest import WSGIRequest
		from submin.dispatch.dispatcher import dispatcher
		self.WSGIRequest = WSGIRequest
		self.dispatcher = dispatcher

	def __del__(self):
		self.storage.close()

	def __iter__(self):
		try:
			req = self.WSGIRequest(self.environ)
			response = self.dispatcher(req)
			self.start_response(response.status(), response.headers.items())
			content = response.encode_content()
		except Exception as e:
			import traceback
			trace = traceback.extract_tb(sys.exc_info()[2])
			list = traceback.format_list(trace)
			list.append(str(e))
			self.start_response('500 Not Ok', [])
			content = ''.join(list)
		
		yield content

application = Application
