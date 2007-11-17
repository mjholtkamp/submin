from mod_python import apache, Cookie, util
from lib.utils import mimport
import os, sys

def handler(req):
	req.content_type = 'text/html; charset=UTF-8'
	
	# Autoreloading main module. Maybe I need a wrapper for this one, this is ugly.
	#modSite = apache.import_module('lib.site', autoreload=True)

	modSite = mimport('lib.site')
	site = modSite.Site(req)
	return site.handler()
