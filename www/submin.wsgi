#!/usr/bin/python
import os
import sys

def application(environ, start_response):
	if not environ.has_key('SUBMIN_ENV'):
		start_response('200 ok', [])
		return 'Please set SUBMIN_ENV in your apache config (ie. via SetEnv)'
	os.environ['SUBMIN_ENV'] = environ['SUBMIN_ENV']

	# __file__ contains <submin-dir>/www/submin.wsgi
	submin_www_dir = os.path.dirname(__file__)
	submin_dir = os.path.dirname(submin_www_dir)
	sys.path.append(os.path.join(submin_dir, 'lib'))
	from models import backend

	backend.open()
	os.chdir(submin_www_dir) # same behaviour as CGI script

	try:
		from dispatch.wsgirequest import WSGIRequest
		from dispatch import dispatcher

		req = WSGIRequest(environ)
		response = dispatcher(req)
		start_response(response.status(), response.headers.items())

		content = ''.join(response.content.encode('utf-8'))

		backend.close()

		return content
	except Exception, e:
		import traceback
		trace = traceback.extract_tb(sys.exc_info()[2])
		list = traceback.format_list(trace)
		list.append(str(e))
		start_response('500 Not Ok', [])
		return ''.join(list)

