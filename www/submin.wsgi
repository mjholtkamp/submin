#!/usr/bin/python

def application(environ, start_response):
	import os
	import sys
	if not environ.has_key('SUBMIN_ENV'):
		start_response('200 ok', [])
		return 'Please set SUBMIN_ENV in your apache config (ie. via SetEnv)'

	try:
		os.environ['SUBMIN_ENV'] = environ['SUBMIN_ENV']
		# __file__ contains <submin-dir>/www/submin.wsgi
		submindir = os.path.dirname(os.path.dirname(__file__))
		sys.path.append(os.path.join(submindir, 'lib'))
		from models import backend

		backend.open()

		from dispatch.wsgirequest import WSGIRequest
		from dispatch import dispatcher

		req = WSGIRequest(environ)
		response = dispatcher(req)
		start_response(response.status(), response.headers.items())
		content = response.content.encode('utf-8')

		backend.close()

		return [content]
	except Exception, e:
		import traceback
		trace = traceback.extract_tb(sys.exc_info()[2])
		list = traceback.format_list(trace)
		list.append(str(e))
		start_response('500 Not Ok', [])
		return list

