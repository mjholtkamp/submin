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
	def __init__(self):
		Response.__init__(self)
		self.status_code = 404
		self.content = 'Page not found.'
