#!/usr/bin/python

import md5crypt
import fcntl
from fcntl import LOCK_EX
from os import rename

class HTPasswd:
	def __init__(self, file):
		self.htpasswd_file = file
		self.modified = False  # have we modified ourselves?
		self.fd = open(self.htpasswd_file, 'r')
		self.lock()

		self.passwords = dict()
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
			rename(self.htpasswd_file, self.htpasswd_file + '.old')
			rename(self.htpasswd_file + '.bak', self.htpasswd_file)
			self.modified = False

	def check(self, user, password):
		""" Check if user has password """
		if not self.passwords.has_key(user):
			return False

		magic, salt, encrypted = self.passwords[user][1:].split('$')

		hash = md5crypt.md5crypt(password, salt, '$' + magic + '$')

		return hash == self.passwords[user]

	def change(self, user, password):
		""" Change users password """
		magic, salt, encrypted = self.passwords[user][1:].split('$')

		newhash = md5crypt.md5crypt(password, salt, '$' + magic + '$')

		self.passwords[user] = newhash
		self.modified = True

	def list(self):
		for user, encrypted in self.passwords.iteritems():
			print 'User: ' + user + ' Password: ' + encrypted

	def users(self):
		users = []
		for user in self.passwords.iterkeys():
			users.append(user)
		return users


if __name__ == '__main__':
	htpasswd = HTPasswd('/home/sabre2th/public_html/submerge/.htpasswd.test')
	htpasswd.list()
	if htpasswd.check('sabre2th', 'blabla'):
		print 'correct!'
	else:
		print 'fail!'
	htpasswd.change('sabre2th', 'test')
	htpasswd.flush()
	
