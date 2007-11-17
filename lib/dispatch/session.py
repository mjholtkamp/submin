import cPickle
import time
import os
import thread
import md5

from config.config import Config

class SessionDestroyedError(Exception):
	"""If a session is destroyed, it cannot be opened or accessed anymore
	"""
	pass


class PickleDict:
	"""Dictionary which stores a dictionary in a file using the cPickle
	library

	If autosave is True (default) PickleDict automatically saves when
	setting a value (using pickledictobject['foo'] = 'bar')
	"""

	def __init__(self, filename, autosave=True):
		try:
			filehandle = open(filename, 'r')
			self.dict = cPickle.load(filehandle)
			filehandle.close()
		except:
			self.dict = {}

		self.autosave = autosave
		self.filename = filename
		self.lock = thread.allocate_lock()
	
	def save(self):
		try:
			self.lock.acquire()
			filehandle = open(self.filename, 'w')
			cPickle.dump(self.dict, filehandle)
			filehandle.close()
		finally:
			self.lock.release()
	
	def __getitem__(self, key):
		return self.dict[key]
	
	def __setitem__(self, key, value):
		self.dict[key] = value
		if self.autosave:
			self.save()

	def get(self, *args, **kwargs):
		return self.dict.get(*args, **kwargs)

	def _destroy(self):
		os.path.unlink(self.filename)


class Session(PickleDict):
	def __init__(self, request, autoupdatecookie=True, autosave=True):
		self.request = request
		self.sessionid = self.request.getCookie('SubminSessionID', \
				self.generateSessionID())
		if autoupdatecookie:
			self.updateCookie()

		self.__destroyed = False
		PickleDict.__init__(self, self.__getfilename(), autosave)

	def __getfilename(self):
		if self.destroyed():
			raise SessionDestroyedError
		return '/tmp/sm-sess%s' % self.sessionid

	def __setitem__(self, *args):
		if self.destroyed():
			raise SessionDestroyedError
		return PickleDict.__setitem__(self, *args)
	
	def __getitem__(self, *args):
		if self.destroyed():
			raise SessionDestroyedError
		return PickleDict.__getitem__(self, *args)
	
	def get(self, *args, **kwargs):
		if self.destroyed():
			raise SessionDestroyedError
		return PickleDict.get(self, *args, **kwargs)

	def destroy(self):
		self.__destroyed = True
		self.request.setCookie('SubminSessionID', 'xx',
				expires=time.asctime())
	
	def destroyed(self):
		return self.__destroyed or self.sessionid == 'xx'

	def updateCookie(self):
		self.request.setCookie('SubminSessionID', self.sessionid)
	
	def generateSessionID(self):
		"""Really an MD5-sum of the current time and a salt"""
		config = Config()
		salt = config.get('generated', 'session_salt')
		return md5.md5(salt + \
				md5.md5(str(time.time())).hexdigest()).hexdigest()
