#!/usr/bin/python
import sys
import os

def application(environ, start_response):
	# __file__ contains <submin-dir>/static/www/submin.wsgi
	submin_www_dir = os.path.dirname(__file__)
	submin_static_dir = os.path.dirname(submin_www_dir)
	submin_dir = os.path.dirname(submin_static_dir)
	os.chdir(submin_www_dir) # same behaviour as CGI script

	from submin.bootstrap import SubminInstallationCheck
	check = SubminInstallationCheck(submin_dir, environ)
	if not check.ok:
		start_response("500 Not Ok", [])
		return check.error_page().encode("utf-8")

	os.environ['SUBMIN_ENV'] = environ['SUBMIN_ENV']

	from submin.models import storage
	storage.open()

	try:
		from submin.dispatch.wsgirequest import WSGIRequest
		from submin.dispatch.dispatcher import dispatcher

		req = WSGIRequest(environ)
		response = dispatcher(req)
		start_response(response.status(), response.headers.items())
		content = response.encode_content()
	except Exception, e:
		import traceback
		trace = traceback.extract_tb(sys.exc_info()[2])
		list = traceback.format_list(trace)
		list.append(str(e))
		start_response('500 Not Ok', [])
		content = ''.join(list)
	
	storage.close()
	return content
