class Response(object):
	def __init__(self, content=''):
		self.content = str(content)
		self.status_code = 200
		self.headers = {'Content-type': 'text/html'}

class Redirect(Response):
	def __init__(self, url):
		Response.__init__(self)
		self.url = url
		self.status_code = 302
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
		self.headers = {'Content-type': 'text/xml'}

class XMLStatusResponse(Response):
	def __init__(self, success, text):
		content = '<response><success>%s</success><text>%s</text></response>' \
			% (success, text)

		Response.__init__(self, content)
