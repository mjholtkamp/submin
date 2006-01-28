import random
from cStringIO import StringIO
from lib.utils import mimport
Buffer = mimport('lib.utils').Buffer
iif = mimport('lib.utils').iif

def header(title = None, scripts = [], css = []):
	html = Buffer()
	try:
		html.write('''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
	<head>
		<title>Submerge%s</title>
		<link rel="stylesheet" type="text/css" href="submerge.css" 
			media="screen" />'''% iif(title, ' - %s' % title, ' '))

		for sheet in css:
			html.write('''\t\t<link rel="stylesheet" type="text/css" href="/media/css/%s.css"
			media="screen" />''' % sheet)

		for script in scripts:
			html.write('''\t\t<script src="/media/js/%s.js" type="text/javascript"></script>''' % script)

		html.write('''
	</head>
	<body>
		<div id="header">
			<h1><a href="/">Submerge</a></h1>
		</div>\
''')

	return str(html)

def footer():
	html = Buffer()
	html.write('''
	</body>
</html>''')

	return str(html)
