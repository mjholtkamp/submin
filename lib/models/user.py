import models
import validators
backend = models.backend.get("user")
UserExistsError = backend.UserExistsError

class UnknownUserError(Exception):
	pass

class User(object):
	@staticmethod
	def list(session_user):
		"""Returns a (sorted) list of users

		list expects a session_user argument: this is the user requesting the
		user list. If the user is not an admin, it will only get to see
		herself.
		"""
		if not session_user.is_admin: # only admins get to see the entire list
			return [session_user]     # users only see themselves

		return [User(raw_data=user) for user in backend.list()]

	@staticmethod
	def add(username, password=None):
		"""Adds a new user with a no password.

		To generate a password, call generate_password()
		Raises UserExistsError if a user with this username already exists.
		"""

		backend.add(username, password)
		return User(username)

	def __init__(self, username=None, raw_data=None):
		"""Constructor, either takes a username or raw data

		If username is provided, the backend is used to get the required data.
		If raw_data is provided, the backend is not used.
		"""
		db_user = raw_data

		if not raw_data:
			db_user = backend.user_data(username)
			if not db_user:
				raise UnknownUserError(username)

		self._id       = db_user['id']
		self._name     = db_user['name']
		self._email    = db_user['email']
		self._fullname = db_user['fullname']
		self._is_admin = db_user['is_admin']

		self.notifications = {}

		self.is_authenticated = False # used by session, listed here to provide
		                              # default value

	def __str__(self):
		return self.name

	def check_password(self, password):
		"""Return True if password is correct, can raise NoMD5PasswordError"""
		return backend.check_password(self._id, password)

	def set_password(self, password):
		backend.set_password(self._id, password)

	def generate_password(self):
		"""generate and return a random password"""
		from string import ascii_letters, digits
		import random
		password_chars = ascii_letters + digits
		password = ''.join([random.choice(password_chars) \
				for x in range(0, 50)])

		self.set_password(password)
		return password

	def remove(self):
		backend.remove_from_groups(self._id)
		backend.remove_permissions_repository(self._id)
		backend.remove_permissions_submin(self._id)
		backend.remove_notifications(self._id)
		backend.remove(self._id)

	def member_of(self):
		return backend.member_of(self._id)

	def nonmember_of(self):
		return backend.nonmember_of(self._id)

	# Properties
	def _getId(self):
		return self._id

	def _getName(self):
		return self._name

	def _setName(self, name):
		self._name = name
		if not validators.validate_username(name):
			raise validators.InvalidUsername(name)
		backend.set_name(self._id, name)

	def _getEmail(self):
		return self._email

	def _setEmail(self, email):
		self._email = email
		if not validators.validate_email(email):
			raise validators.InvalidEmail(email)
		backend.set_email(self._id, email)

	def _getFullname(self):
		return self._fullname

	def _setFullname(self, fullname):
		self._fullname = fullname
		if not validators.validate_fullname(fullname):
			raise validators.InvalidFullname(fullname)
		backend.set_fullname(self._id, fullname)

	def _getIsAdmin(self):
		return self._is_admin

	def _setIsAdmin(self, is_admin):
		self._is_admin = is_admin
		backend.set_is_admin(self._id, is_admin)

	id       = property(_getId)   # id is read-only
	name     = property(_getName,     _setName)
	email    = property(_getEmail,    _setEmail)
	fullname = property(_getFullname, _setFullname)
	is_admin = property(_getIsAdmin,  _setIsAdmin)

__doc__ = """
Backend contract
================

* list()
	Returns a sorted list of users, sorted by username

* add(username, password)
	Adds a new user, raises `UserExistsError` if there already is a user with
	this username

* user_data(username)
	Returns a dictionary with all required user data.
	Returns `None` if no user with this username exists.
	Fields which need to be implemented (with properties?): name, email,
	fullname, is_admin

* check_password(id, password)
	Checks whether the supplied password is valid for a user with userid *id*

* set_password(id, password)
	Sets the password for a user with userid *id* to *password*
	
* remove(userid)
	Removes user with id *userid*. Before a user can be removed, all
	remove_-functions below must have been called. This happens in the model,
	so backend designers need not worry about this restriction.

* remove_from_groups(userid)
	Removes user with id *userid* from groups

* remove_permissions_repository(userid)
	Removes a users repository permissions

* remove_permissions_submin(userid)
	Removes a users submin permissions

* remove_notifications(userid)
	Removes a users notifications

* member_of(userid)
	Returns sorted list of groups a user is member of.

* nonmember_of(userid)
	Returns sorted list of groups a user is not a member of.

* set_email(id, email)
	Sets the email for user with id *id*

* set_fullname(id, fullname)
	Sets the fullname for user with id *id*

* set_is_admin(id, is_admin)
	Sets whether user with id *id* is an admin
"""
