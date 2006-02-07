import random
from cStringIO import StringIO
from lib.utils import mimport
Buffer = mimport('lib.utils').Buffer
iif = mimport('lib.utils').iif

class Html:
	def __init__(self, input):
		self.input = input

	def header(self, title = None, scripts = [], css = []):
		buf = Buffer()
		buf.write('''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
		"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
	<head>
		<title>Submerge%s</title>
		<base href="%s/" />
		<link rel="stylesheet" type="text/css" href="submerge.css" 
			media="screen" />\n'''% \
					(iif(title, ' - %s' % title, ' '), self.input.base))

		for sheet in css:
			buf.write('''\t\t<link rel="stylesheet" type="text/css" href="%s.css" media="screen" />\n''' % \
					sheet)

		for script in scripts:
			buf.write('''\t\t<script src="%s.js" type="text/javascript"></script>\n''' % \
					(script,))

		buf.write('''
	</head>
	<body>
		<div id="header">
			<h1><a href="%s">Submerge</a></h1>
		</div>
		<div class="container">
			<div id="menu">
				<ul>
					Menu
		            <li><a href=".">main page</a></li>
		            <li><a href="profile">profile</a></li>\
''' % self.input.base)

		if self.input.isAdmin():
			buf.write('''
					Admin
					<ul>
					<li><a href="users">users</a></li>
					<li><a href="group">groups</a></li>
		            <li><a href="authz">permissions</a></li>
					</ul>''')

		if self.input.isLoggedIn():
			buf.write('<li><a href="logout">logout</a></li>')
		else:
			buf.write('<li><a href="login">login</a></li>')

		buf.write('''
					<li><a href="https://submerge.air.nl.eu.org/projects/submerge">Trac</a></li>
		        </ul>
			</div>
			<div id="content">''')

		return str(buf)

	def footer(self):
		buf = Buffer()
		buf.write('''
			</div>
		</div>
	</body>
</html>''')

		return str(buf)
