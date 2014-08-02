import urlparse
from submin.models import options

class Response(object):
	def __init__(self, content='', status_message='Ok'):
		self.content = content
		self.status_code = 200
		self.headers = {'Content-Type': 'text/html; charset=utf-8'}
		self.status_message = status_message

	def status(self):
		return str(self.status_code) + ' ' + self.status_message

	def setCookieHeaders(self, cookies):
		self.headers['Set-Cookie'] = cookies

	def encode_content(self):
		return ''.join(self.content.encode('utf-8'))

class FileResponse(Response):
	def __init__(self, content, content_type):
		Response.__init__(self, content)
		self.headers.update({'Content-Type': content_type})

	def encode_content(self):
		# because these are files, don't encode
		return self.content

class Redirect(Response):
	def __init__(self, url, request, store_url=True):
		Response.__init__(self, status_message='The princess is in another castle')
		if not request.is_ajax() and store_url:
			request.session['redirected_from'] = request.url

		if not store_url and 'redirected_from' in request.session:
			del request.session['redirected_from']

		url = unicode(url)
		self.status_code = 302
		if '://' not in url:
			vhost = options.value("http_vhost")
			if '://' not in vhost:
				vhost = 'http://' + vhost

			# to prevent accidental double slashes to be interpreted as netloc,
			# we strip all leading slashes from the url
			url = urlparse.urljoin(vhost, url.lstrip('/'))

		self.headers.update({'Location': url.encode('utf-8')})

class HTTP404(Response):
	def __init__(self, page='/'):
		error_msg = 'Page %s not found.' % page
		Response.__init__(self, error_msg, 'Not Found')
		self.status_code = 404

class HTTP500(Response):
	def __init__(self, content):
		error_msg = 'Internal Server Error'
		Response.__init__(self, error_msg, error_msg)
		self.status_code = 500

class TeapotResponse(Response):
	def __init__(self, content):
		Response.__init__(self, content, "I'm a teapot")
		self.status_code = 418

class XMLResponse(Response):
	def __init__(self, content):
		content = \
			'''<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
''' + \
			content

		Response.__init__(self, content)
		self.headers = {'Content-Type': 'text/xml', 'Cache-Control': 'no-cache'}

class XMLStatusResponse(XMLResponse):
	def __init__(self, command, success, text, details=None):
		from submin.template.shortcuts import evaluate
		tvars = {'command': command, 'success_str': str(success), 'text': text,
				'details': details, 'success': success}
		content = evaluate('ajax/response.xml', tvars)

		XMLResponse.__init__(self, content)

class XMLTemplateResponse(XMLResponse):
	def __init__(self, template, templatevariables):
		from submin.template.shortcuts import evaluate
		content = evaluate(template, templatevariables)

		XMLResponse.__init__(self, content)
