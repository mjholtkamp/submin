from mod_python import apache, util
from lib.utils import mimport
import sys
import ConfigParser
html = mimport('lib.html')
Buffer = mimport('lib.utils').Buffer
exceptions = mimport('lib.exceptions')
log = mimport('lib.log')
mod_authz = mimport('lib.authz')
from mod_python import Session

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


class Input:
	def __init__(self, get, post, req, pathInfo):
		self.req = req;

		self.get = get; 
		self.post = post; 
		self.pathInfo = pathInfo; 

		self.base = self.absolutePath(self.__base())

		self.config = self.__getConfig()
		self.authz = self.__getAuthz()

		self.html = html.Html(self)
		self.session = Session.Session(req)

		self.user = None
		if self.isLoggedIn():
			self.user = self.session['user']

	def isLoggedIn(self):
		if self.session.has_key('user'):
			return True
		return False

	def saveSession(self, user):
		self.session['user'] = user
		self.user = user
		self.session.save()

	def deleteSession(self):
		self.session.delete()
		self.session.invalidate()
		self.user = None

	def isAdmin(self):
		"""Check if current user is in the submerge-admins group"""
		try:
			admins = self.authz.members('submerge-admins')
			return self.user in admins
		except mod_authz.UnknownGroupError:
			return False

	def __getAuthz(self):
		try:
			authz_file = self.config.get('svn', 'authz_file')
		except ConfigParser.NoSectionError, e:
			raise Exception, str(e) + 'in' + str(SubmergeEnv)

		return mod_authz.Authz(authz_file)

	def __getConfig(self):
		SubmergeEnv = self.req.get_options()['SubmergeEnv']

		cp = ConfigParser.ConfigParser()
		cp.read(SubmergeEnv)

		return cp

	def __base(self):
		filename = self.req.uri
		path_info = '/submerge.py%s' % (self.req.path_info or '')
		index = self.req.uri.rindex(path_info)
		if not index:
			return '/'
		filename = filename[:index]
		return filename

	# taken from trac, maybe we need to write our own method for this? :)
	def absolutePath(self, path=None):
		host = self.req.headers_in.get('Host')

		scheme = 'http'
		if self.req.subprocess_env.get('HTTPS') in ('on', '1') \
				or self.server_port == 443:
			scheme = 'https'


		if self.req.headers_in.get('X-Forwarded-Host'):
			host = self.req.headers_in.get('X-Forwarded-Host')
		if not host:
			# Missing host header, so reconstruct the host from the
			# server name and port
			default_port = {'http': 80, 'https': 443}

			if self.req.connection.local_addr[1] and \
					self.req.connection.local_addr[1] != default_port[scheme]:
				host = '%s:%d' % (self.req.server.server_hostname, \
						self.req.connection.local_addr[1])
			else:
				host = self.req.server.server_hostname

		if not path:
			if len(self.pathInfo):
				path = self.req.uri[:-len(self.pathInfo)] or '/'
			else:
				path = self.req.uri

		import urlparse
		return urlparse.urlunparse((scheme, host, path, None, None, None))


class Site:
	def __init__(self, req):
		# create own version of request, for in CGI-environment?
		self.req = req

		# Replace stdout with a buffer for use with print
		self.buffer = Buffer()
		sys.stdout = self.buffer

		self.loglevels = dict(
				ex=log.addlevel('Exception'),
				)

		# move this to Input instance?
		self.ip = self.req.get_remote_host()

		self.pathInfo = PathInfo(self.req.path_info.strip('/').split('/'))
		if self.req.args:
			self.get = util.parse_qs(self.req.args) # <type 'Dict'>
		else:
			self.get = {}
		self.post = Post(self.req)

	def handler(self):
		returnValue = None

		page = self.getPageMod()
		if not page: return apache.HTTP_NOT_FOUND

		self.req.headers_out.add("Cache-control", "no-cache")

		input = Input(self.get, self.post, self.req, self.pathInfo)

		if hasattr(page, 'login_required') and page.login_required:
			if input.session.is_new():
	 			util.redirect(self.req, '%slogin' % input.base)
				return apache.OK

		if hasattr(page, 'admin') and page.admin and not input.isAdmin():
			buffer = Buffer()
			buffer.write(
					input.html.header('Error'),
					'''<h1>Error</h1><p>Sorry, you don't have permission to
					access this page</p>''',
					input.html.footer())
			self.req.write(str(buffer))
			return apache.OK

		if len(self.pathInfo) >= 2 and hasattr(page, self.pathInfo[1]):
			func = getattr(page, self.pathInfo[1])
		else:
			func = page.handler

		try:
			returnValue = func(input)
			if not str(self.buffer):
				return apache.HTTP_NOT_FOUND

			self.req.write(str(self.buffer))
			if not returnValue:
				return apache.OK
			return returnValue
		except exceptions.error, e:
			buffer = Buffer()
			buffer.write(
					input.html.header('Error'),
					'''<h1>Error</h1>
					   <p>An error occurred:</p>
					   <pre>%s</pre>''' % e,
					input.html.footer())
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
