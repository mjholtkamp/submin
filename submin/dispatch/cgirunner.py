import sys
import os

def run():
	# __file__ contains <submin-dir>/dispatch/cgirunner.py
	submin_www_dir = os.path.dirname(__file__)
	submin_dir = os.path.dirname(submin_www_dir)

	from submin.bootstrap import SubminInstallationCheck
	check = SubminInstallationCheck(submin_dir)
	if not check.ok:
		print "Status: 500\r\n\r\n",
		print check.error_page()
		sys.exit(0)

	from submin.models import storage
	storage.open()

	try:
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

	storage.close()
