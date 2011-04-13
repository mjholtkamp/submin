import urlparse

class Response(object):
	def __init__(self, content=''):
		self.content = content
		self.status_code = 200
		self.headers = {'Content-Type': 'text/html; charset=utf-8'}

	def status(self):
		# XXX provide a real status message
		return str(self.status_code) + ' status'

	def setCookieHeaders(self, cookies):
		self.headers['Set-Cookie'] = cookies

class Redirect(Response):
	def __init__(self, url, request):
		Response.__init__(self)
		url = str(url)
		self.status_code = 302
		if not '://' in url:
			schema = 'https://' if request.https else 'http://'
			url = urlparse.urljoin(schema + request.http_host, url)
		self.headers.update({'Location': url})

class HTTP404(Response):
	def __init__(self, page='/'):
		Response.__init__(self)
		self.status_code = 404
		self.content = 'Page %s not found.' % page

class HTTP500(Response):
	def __init__(self, content):
		Response.__init__(self, content)
		self.status_code = 500

class XMLResponse(Response):
	def __init__(self, content):
		content = \
			'''<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
''' + \
			content

		Response.__init__(self, content)
		self.headers = {'Content-Type': 'text/xml', 'Cache-Control': 'no-cache'}

class XMLStatusResponse(XMLResponse):
	def __init__(self, command, success, text):
		from submin.template.shortcuts import evaluate
		tvars = {'command': command, 'success': str(success), 'text': text}
		content = evaluate('ajax/response.xml', tvars)

		XMLResponse.__init__(self, content)

class XMLTemplateResponse(XMLResponse):
	def __init__(self, template, templatevariables):
		from submin.template.shortcuts import evaluate
		content = evaluate(template, templatevariables)

		XMLResponse.__init__(self, content)
