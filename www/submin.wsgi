#!/usr/bin/python

def application(environ, start_response):
	import os
	import sys
	if not environ.has_key('SUBMIN_CONF'):
		return 'Please set SUBMIN_CONF via SetEnv'

	try:
		os.environ['SUBMIN_CONF'] = environ['SUBMIN_CONF']
		cwd = environ['DOCUMENT_ROOT']
		libdir = os.path.realpath(os.path.join(cwd, '../lib/'))
		os.environ['SCRIPT_FILENAME'] = os.path.join(cwd, 'submin.wsgi')
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
		return [response.content]
	except Exception, e:
		import traceback
		trace = traceback.extract_tb(sys.exc_info()[2])
		list = traceback.format_list(trace)
		list.append(str(e))
		raise str(list)
		start_response('500 Not Ok', [])
		return list

