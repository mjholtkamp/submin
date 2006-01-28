from mod_python import apache, util
from lib.utils import mimport
import sys
html = mimport('lib.html')
Buffer = mimport('lib.utils').Buffer
exceptions = mimport('lib.exceptions')
log = mimport('lib.log')

class PathInfo(list):
	def get(self, idx, default=None):
		try:
			return list.__getitem__(self, idx)
		except IndexError:
			return default

def Post(req):
	"""My own fieldstorage thingie. I didn't like that the fieldstorage items
	   weren't strings.
	"""
	fs = util.FieldStorage(req)
	post = {}
	for key in fs.keys():
		if hasattr(fs[key], 'append'):
			# List
			post[key] = []
			for item in fs[key]:
				if hasattr(item, 'strip'):
					post[key].append(str(item))
				else:
					post[key].append(item)
		elif hasattr(fs[key], 'strip'):
			# string
			post[key] = str(fs[key])
		else:
			post[key] = fs[key]
	return post

class Site:
	def __init__(self, req):
		self.req = req
		self.buffer = Buffer()
		sys.stdout = self.buffer

		#log.open(open('/usr/local/submerge/log/exceptions.log', 'a+'))
		self.loglevels = dict(
				ex=log.addlevel('Exception'),
				)

		self.ip = self.req.get_remote_host()

		self.pathInfo = PathInfo(self.req.path_info.strip('/').split('/'))
		if self.req.args:
			self.get = util.parse_qs(self.req.args) # <type 'Dict'>
		else:
			self.get = {}
		self.post = Post(self.req)

	def handler(self):
		#buffer = Buffer()

		returnValue = None

		page = self.getPageMod()
		if not page: return apache.HTTP_NOT_FOUND

		if hasattr(page, 'login') and page.login:
			buffer.write(
					html.header('Error'),
					'''<h1>Error</h1><p>Sorry, login is not coded yet ;)</p>''',
					html.footer())
			return apache.OK

		if len(self.pathInfo) >= 2 and hasattr(page, self.pathInfo[1]):
			func = getattr(page, self.pathInfo[1])
		else:
			func = page.handler

		try:
			class Input:
				def __init__(self, get, post, req, pathInfo):
					self.get = get; self.post = post; self.req = req;
					self.pathInfo = pathInfo;

			returnValue = func(Input(self.get, self.post, self.req, self.pathInfo))
			if not str(self.buffer):
				return apache.HTTP_NOT_FOUND

			self.req.write(str(self.buffer))
			if not returnValue:
				return apache.OK
			return returnValue
		except exceptions.error, e:
			buffer = Buffer()
			buffer.write(
					html.header('Error'),
					'''<h1>Error</h1>
					   <p>An error occurred:</p>
					   <pre>%s</pre>''' % e,
					html.footer())
			self.req.write(str(buffer))
			return apache.OK
		except exceptions.Redirect, url:
			if not str(url):
				url =  '/'
			util.redirect(self.req, str(url))
		#except Exception, e:
			# Get the traceback and log it to file
			#import traceback
			#buffer = Buffer()
			#traceback.print_exc(file=buffer)
			#log.log(self.ip, str(buffer), self.loglevels['ex'])

			# Output a friendly message
			#buffer = Buffer()
			#buffer.write(
			#		html.header('Error'),
			#		'''<h1>Error</h1>
			#		<p>An error occurred, and the error message was logged.
			#		If you'd like to notify the webmaster, mail him at
			#		webmaster (at) avaeq.nl</p>''',
			#		html.footer())
			#self.req.write(str(buffer))
			return apache.OK

	def getPageMod(self):
		page = 'index'
		if self.pathInfo and self.pathInfo[0]:
			page = self.pathInfo[0]

		try: module = mimport('page.' + page)
		except ImportError: return None

		return module
