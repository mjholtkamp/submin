#!/usr/bin/python
import sys
import os

def application(environ, start_response):
	# __file__ contains <submin-dir>/www/submin.wsgi
	submin_www_dir = os.path.dirname(__file__)
	submin_dir = os.path.dirname(submin_www_dir)
	sys.path.append(os.path.join(submin_dir, 'lib'))
	os.chdir(submin_www_dir) # same behaviour as CGI script

	from bootstrap import SubminInstallationCheck
	check = SubminInstallationCheck(submin_dir)
	if not check.ok:
		start_response("500", [])
		return check.error_page()
		sys.exit(0)

	os.environ['SUBMIN_ENV'] = environ['SUBMIN_ENV']

	from models import backend
	backend.open()

	try:
		from dispatch.wsgirequest import WSGIRequest
		from dispatch.dispatcher import dispatcher

		req = WSGIRequest(environ)
		response = dispatcher(req)
		start_response(response.status(), response.headers.items())
		content = ''.join(response.content.encode('utf-8'))
	except Exception, e:
		import traceback
		trace = traceback.extract_tb(sys.exc_info()[2])
		list = traceback.format_list(trace)
		list.append(str(e))
		start_response('500 Not Ok', [])
		content = ''.join(list)
	
	backend.close()
	return content
