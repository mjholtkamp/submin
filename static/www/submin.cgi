#!/usr/bin/python
import sys
import os
# __file__ contains <submin-dir>/www/submin.cgi
submin_www_dir = os.path.dirname(__file__)
submin_dir = os.path.dirname(submin_www_dir)
sys.path.append(os.path.join(submin_dir, 'lib'))

from submin.bootstrap import SubminInstallationCheck
check = SubminInstallationCheck(submin_dir)
if not check.ok:
	print "Status: 500\r\n\r\n",
	print check.error_page()
	sys.exit(0)

from submin.models import backend
backend.open()

try:
	import cgitb; cgitb.enable()
	from submin.dispatch.cgirequest import CGIRequest
	from submin.dispatch.dispatcher import dispatcher

	req = CGIRequest()
	response = dispatcher(req)
	req.writeResponse(response)
except Exception, e:
	import traceback
	trace = traceback.extract_tb(sys.exc_info()[2])
	list = traceback.format_list(trace)
	list.append(str(e))
	print "Status: 500\r\n\r\n",
	print ''.join(list)

backend.close()
