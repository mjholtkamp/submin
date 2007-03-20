class Request(object):
	def __init__(self):
		self.post = {}
		self.get = {}
		self.path_info = ''
		self.remote_address = ''
		self.headers = {'Content-Type': 'text/html'}
	
	def setHeader(self, header, value):
		self.headers[header] = value
		
	def setHeaders(self, headers={}):
		for header, value in headers.iteritems():
			self.setHeader(header, value)
	
	def writeHeaders(self):
		raise NotImplementedError
	
	def write(self, content):
		raise NotImplementedError