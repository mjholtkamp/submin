from Cookie import SimpleCookie

class Request(object):
	"""Provide a consistent way to treat a Request."""
	
	def __init__(self):
		self.post = {}
		self.get = {}
		self.path_info = ''
		self.remote_address = ''
		self.headers = {'Content-Type': 'text/html'}
		
		self.__incookies = SimpleCookie()
		self.__outcookies = SimpleCookie()
	
	def setHeader(self, header, value):
		self.headers[header] = value
		
	def setHeaders(self, headers={}):
		for header, value in headers.iteritems():
			self.setHeader(header, value)
	
	def setCookieHeaders(self):
		for name in self.__outcookies.keys():
			path = self.__outcookies[name].get('path')
			if path:
				path = path.replace(' ', '%20') \
						.replace(';', '%3B') \
						.replace(',', '%3C')
			self.__outcookies[name]['path'] = path

		cookies = self.__outcookies.output(header='')
		for cookie in cookies.splitlines():
			self.setHeader('Set-Cookie', cookie.strip())
	
	def write(self, content):
		raise NotImplementedError
		
	def status(self, statusCode=200):
		self.write('Status: %d\r\n' % statusCode)

	def writeHeaders(self):
		self.setCookieHeaders()
		for header, value in self.headers.iteritems():
			self.write('%s: %s\r\n' % (header, value))
		self.write('\r\n');
	
	def setCookie(self, key, value, path='/', expires=None):
		self.__outcookies[key] = value
		self.__outcookies[key]['path'] = path
		if expires:
			self.__outcookies[key]['expires'] = expires
	
	def getCookie(self, key, default=None):
		try:
			value = self.__incookies[key]
		except KeyError:
			return default
			
		if not value.value:
			return default
		
		return value.value
		
class NoneObject:
	pass

class GetVariables(object):
	"""Provide a consistent way to access the GET variables."""
	
	def __init__(self, query_string=''):
		"""This is the method that needs to be overridden in CGIGet and 
		ModPythonGet. Each uses a different way to parse the query string"""
		self.variables = [query_string]
	
	def get(self, item, default=NoneObject):
		"""Return just one item from the query string (the last), 
		instead of a list with all the variables"""
		value = self.variables.get(item, [default])
		if value == [NoneObject]:
			raise KeyError(item)
		return value[-1]
	
	def __getitem__(self, item):
		return self.get(item)
	
	def getall(self, item):
		return self.variables.get(item)