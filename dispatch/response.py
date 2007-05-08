class Response(object):
	def __init__(self, content):
		self.content = str(content)
		self.status_code = 200
		self.headers = {}
		
class Redirect(Response):
	def __init__(self, url):
		self.url = url
		self.status_code = 302
		self.headers = {'Location': url}

class HTTP404(Response):
	def __init__(self):
		self.status_code = 404