#!/usr/bin/python

import md5crypt
import fcntl
from fcntl import LOCK_EX
from os import rename, unlink

class HTPasswd:
	def __init__(self, file):
		self.passwords = dict()
		self.htpasswd_file = file
		self.modified = False  # have we modified ourselves?
		try:
			self.fd = open(self.htpasswd_file, 'r')
		except IOError:
			open(self.htpasswd_file, 'a')
			return

		self.lock()

		for line in self.fd.readlines():
			user, encrypted = line.rstrip().split(':')
			self.passwords[user] = encrypted

		self.fd.close()

	def __del__(self):
		self.flush()

	def lock(self):
		""" Lock the password file, will unlock at close """
		fcntl.flock(self.fd, LOCK_EX)

	def flush(self):
		""" Write changes to disk """
		if self.modified:
			fd = open(self.htpasswd_file + '.bak', 'w')
			for user, encrypted in self.passwords.iteritems():
				fd.write(user + ':' + encrypted + '\n')
			fd.close() # fd.close just returns a pointer to the function - avaeq
			unlink(self.htpasswd_file)
			rename(self.htpasswd_file + '.bak', self.htpasswd_file)
			self.modified = False

	def exists(self, user):
		""" Check if user exists """
		if not self.passwords.has_key(user):
			return False
		return True

	def check(self, user, password):
		""" Check if user has password """
		if not self.passwords.has_key(user):
			return False

		magic, salt, encrypted = self.passwords[user][1:].split('$')

		hash = md5crypt.md5crypt(password, salt, '$' + magic + '$')

		return hash == self.passwords[user]

	def change(self, user, password):
		""" Change users password """
		if not self.passwords.has_key(user):
			return False

		magic, salt, encrypted = self.passwords[user][1:].split('$')

		newhash = md5crypt.md5crypt(password, salt, '$' + magic + '$')

		self.passwords[user] = newhash
		self.modified = True

	def users(self):
		""" Returns a list of all users """
		users = []
		for user in self.passwords.iterkeys():
			users.append(user)
		return users

	def add(self, user, password):
		""" Add/overwrite a new user """
		magic = 'apr1'
		salt = md5crypt.makesalt()
		newhash = md5crypt.md5crypt(password, salt, '$' + magic + '$')

		self.passwords[user] = newhash
		self.modified = True
		self.flush()
	
	def remove(self, user):
		""" Remove a user """
		if not self.passwords.has_key(user):
			return False

		del self.passwords[user]
		self.modified = True

if __name__ == '__main__':
	htpasswd = HTPasswd('/tmp/.htpasswd.test')
	htpasswd.add('test', 'test')
	htpasswd.list()
	if htpasswd.check('test', 'test'):
		print 'correct!'
	else:
		print 'fail!'
	htpasswd.change('test', 'test!')
	htpasswd.flush()

