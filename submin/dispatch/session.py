import json
import time
import os
import thread
from hashlib import md5
from submin.models import options

class SessionDestroyedError(Exception):
	"""If a session is destroyed, it cannot be opened or accessed anymore
	"""
	pass


class PickleDict(object):
	"""Dictionary which stores a dictionary in a file using the json
	library

	If autosave is True (default) PickleDict automatically saves when
	setting a value (using pickledictobject['foo'] = 'bar')
	"""

	def __init__(self, autosave=True):
		self.autosave = autosave
		self.dict = {} # default
		self.load()

	def save(self):
		raise NotImplementedError

	def __contains__(self, key):
		return key in self.dict

	def __getitem__(self, key):
		return self.dict[key]

	def __setitem__(self, key, value):
		self.dict[key] = value
		if self.autosave:
			self.save()

	def __delitem__(self, key):
		del self.dict[key]
		if self.autosave:
			self.save()

	def get(self, *args, **kwargs):
		return self.dict.get(*args, **kwargs)

	def _destroy(self):
		os.path.unlink(self.filename)

class FilePickleDict(PickleDict):
	def __init__(self, filename, autosave=True):
		self.filename = filename
		self.lock = thread.allocate_lock()
		super(FilePickleDict, self).__init__(autosave)

	def load(self):
		try:
			filehandle = open(self.filename, 'r')
			self.dict = json.load(filehandle)
			filehandle.close()
		except:
			pass

	def save(self):
		try:
			self.lock.acquire()
			filehandle = open(self.filename, 'w')
			json.dump(self.dict, filehandle)
			filehandle.close()
		finally:
			self.lock.release()

class DBPickleDict(PickleDict):
	def __init__(self, key, autosave=True):
		self.key = key
		super(DBPickleDict, self).__init__(autosave)

	def load(self):
		from submin.models import sessions
		from submin.models.exceptions import UnknownKeyError
		try:
			val = sessions.value(self.key)
			self.dict = json.loads(str(val))
		except UnknownKeyError:
			pass
		except ValueError:
			# invalid (old) session, invalidate
			self.dict = {}
			sessions.unset_value(self.key)

	def save(self):
		from submin.models import sessions
		val = json.dumps(self.dict)
		sessions.set_value(self.key, val)


SESS_CLASS = DBPickleDict
SESS_INIT_ARG = "_getid"
from submin.models.storage import database_isuptodate
if not database_isuptodate():
	SESS_CLASS = FilePickleDict
	SESS_INIT_ARG = "_getfilename"


class Session(SESS_CLASS):
	def __init__(self, request, autoupdatecookie=True, autosave=True):
		self.request = request
		self.sessionid = self.request.getCookie('SubminSessionID', \
				self.generateSessionID())
		if autoupdatecookie:
			self.updateCookie()

		self.__destroyed = False
		init_arg = getattr(self, SESS_INIT_ARG)
		super(Session, self).__init__(init_arg(), autosave)

	def _getfilename(self):
		if self.destroyed():
			raise SessionDestroyedError
		suffix = md5(str(options.url_path('base_url_submin'))).hexdigest()
		return '/tmp/sm-sess%s-%s' % (self.sessionid, suffix)

	def _getid(self):
		return self.sessionid

	def __setitem__(self, *args):
		if self.destroyed():
			raise SessionDestroyedError
		return super(Session, self).__setitem__(*args)

	def __delitem__(self, *args):
		if self.destroyed():
			raise SessionDestroyedError
		return super(Session, self).__delitem__(*args)

	def __contains__(self, *args):
		if self.destroyed():
			raise SessionDestroyedError
		return super(Session, self).__contains__(*args)

	def __getitem__(self, *args):
		if self.destroyed():
			raise SessionDestroyedError
		return super(Session, self).__getitem__(*args)

	def get(self, *args, **kwargs):
		if self.destroyed():
			raise SessionDestroyedError
		return super(Session, self).get(*args, **kwargs)

	def destroy(self):
		self.__destroyed = True
		self.request.setCookie('SubminSessionID', 'xx',
				expires=time.asctime())

	def destroyed(self):
		return self.__destroyed or self.sessionid == 'xx'

	def updateCookie(self):
		base_url = str(options.url_path('base_url_submin'))
		http = 'http://'
		if http in base_url:
			try:
				base_url = base_url[base_url.index('/', len(http)):]
			except ValueError:
				# ok, this is weird, apparently, base_url is just a hostname
				# assume virtual_host specifically for submin
				base_url = '/'

		self.request.setCookie('SubminSessionID', self.sessionid, \
			str(base_url))

	def generateSessionID(self):
		"""Really an MD5-sum of the current time and a salt"""
		from submin.models import options
		salt = options.value('session_salt')
		return md5(salt + \
				md5(str(time.time())).hexdigest()).hexdigest()
