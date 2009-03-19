#!/usr/bin/python

def application(environ, start_response):
	import os
	import sys
	if not environ.has_key('SUBMIN_CONF'):
		start_response('200 ok', [])
		return 'Please set SUBMIN_CONF in your apache config (ie. via SetEnv)'

	try:
		os.environ['SUBMIN_CONF'] = environ['SUBMIN_CONF']
		os.environ['SCRIPT_FILENAME'] = environ['SCRIPT_FILENAME']
		cwd = os.path.dirname(environ['SCRIPT_FILENAME'])
		libdir = os.path.realpath(os.path.join(cwd, '../lib/'))
		sys.path.append(libdir)
		from dispatch.wsgirequest import WSGIRequest
		from dispatch import dispatcher

		""" Call reinit, to see if files are changed. (bug #100). """
		from config.config import Config
		config = Config()
		config.reinit()

		req = WSGIRequest(environ)
		response = dispatcher(req)
		start_response(response.status(), response.headers.items())
		return [response.content.encode('utf-8')]
	except Exception, e:
		import traceback
		trace = traceback.extract_tb(sys.exc_info()[2])
		list = traceback.format_list(trace)
		list.append(str(e))
		raise str(list)
		start_response('500 Not Ok', [])
		return list

