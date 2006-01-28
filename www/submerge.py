from mod_python import apache, Cookie, util
import os, sys

def handler(req):
	req.content_type = 'text/html; charset=UTF-8'
	
	# Autoreloading main module. Maybe I need a wrapper for this one, this is ugly.
	modSite = apache.import_module('lib.site', autoreload=True)
	site = modSite.Site(req)
	return site.handler()
