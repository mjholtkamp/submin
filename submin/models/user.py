from submin import models
from submin.hooks.common import trigger_hook
from submin.models import options
from submin.models import repository
import validators
storage = models.storage.get("user")

from submin.models.exceptions import UnknownUserError, UserPermissionError

class FakeAdminUser(object):
	"""Sometimes you have no session_user but you want to make a change to
	a user where admin rights are needed. You can pass an instance of this
	object as 'session_user' to get admin rights."""
	def __init__(self):
		self.is_admin = True

def list(session_user):
	"""Returns a (sorted) list of usernames

	list expects a session_user argument: this is the user requesting the
	user list. If the user is not an admin, it will only get to see
	herself.
	"""
	if not session_user.is_admin: # only admins get to see the entire list
		return [session_user.name]     # users only see themselves

	return [user['name'] for user in storage.list()]

def add(username, email, password=None, send_mail=True, origin=None):
	"""Adds a new user

	If password is not set, send an email to supplied address with activation
	link. Raises UserExistsError if a user with this username already exists.
	"""
	if not validators.validate_username(username):
		raise validators.InvalidUsername(username)

	if not validators.validate_email(email):
		raise validators.InvalidEmail(email)

	storage.add(username, password)
	trigger_hook('user-create', username=username, user_passwd=password)
	u = User(username)
	u.email = email
	if not password and send_mail:
		u.prepare_password_reset(origin)

	return u

class User(object):
	def __init__(self, username=None, raw_data=None):
		"""Constructor, either takes a username or raw data

		If username is provided, the storage plugin is used to get the
		required data. If raw_data is provided, the storage plugin is not used.
		"""
		db_user = raw_data
		
		if not username and not raw_data:
			raise ValueError('Both username and raw_data are unset')

		if not raw_data:
			db_user = storage.user_data(username)
			if not db_user:
				raise UnknownUserError(username)

		self._type     = 'user' # needed for Manager
		self._id       = db_user['id']
		self._name     = db_user['name']
		self._email    = db_user['email']
		self._fullname = db_user['fullname']
		self._is_admin = db_user['is_admin']

		self.is_authenticated = False # used by session, listed here to provide
		                              # default value

	def __str__(self):
		return unicode(self).encode('utf-8')

	def __unicode__(self):
		return self._name

	def session_object(self):
		return {'name': self._name, 'is_admin': self._is_admin, 
				'is_authenticated': self.is_authenticated}

	def check_password(self, password):
		"""Return True if password is correct, can raise NoMD5PasswordError"""
		return storage.check_password(self._id, password)

	def set_password(self, password, send_email=False):
		storage.set_password(self._id, password)
		trigger_hook('user-update', username=self._name, user_passwd=password)
		if send_email:
			self.email_user(password=password)

	def get_password_hash(self):
		return storage.get_password_hash(self._id)

	def set_md5_password(self, password):
		storage.set_md5_password(self._id, password)

	def generate_random_string(self, length=50):
		"""generate and return a random string"""
		from string import ascii_letters, digits
		import random
		string_chars = ascii_letters + digits
		string = ''.join([random.choice(string_chars) \
				for x in range(0, length)])

		return string

	def prepare_password_reset(self, origin):
		key = self.generate_random_string()
		storage.set_password_reset_key(self._id, key)
		self.email_user(key=key, origin=origin)

	def valid_password_reset_key(self, key):
		"""Validate password request for this user."""
		return storage.valid_password_reset_key(self._id, key)

	def clear_password_reset_key(self):
		storage.clear_password_reset_key(self._id)

	def email_user(self, key=None, password=None, origin=None):
		"""Email the user a key (to reset her password) OR a password (if the
		user followed a link with the key in it). The origin shows where the request
		came from (string)"""
		from submin.template.shortcuts import evaluate
		from submin.email import sendmail
		
		if key and password:
			raise ValueError('Ambiguous input: both key and password are set')

		templatevars = {
			'from': options.value('smtp_from', 'root@localhost'),
			'to': self.email,
			'username': self.name,
			'key': key,
			'password': password,
			'http_vhost': options.http_vhost(),
			'base_url': options.url_path("base_url_submin"),
			'origin': origin,
		}
		if key:
			template = 'email/prepare_reset.txt'
		else:
			template = 'email/reset_password.txt'
		
		message = evaluate(template, templatevars)
		sendmail(templatevars['from'], templatevars['to'], message)

	def remove(self):
		storage.remove_from_groups(self._id)
		storage.remove_permissions_repository(self._id)
		storage.remove_permissions_submin(self._id)
		storage.remove_notifications(self._id)
		storage.remove_all_ssh_keys(self._id)
		storage.remove(self._id)
		trigger_hook('user-delete', username=self._name)

	def member_of(self):
		return storage.member_of(self._id)

	def nonmember_of(self):
		return storage.nonmember_of(self._id)

	def set_notifications(self, notifications, session_user):
		"""notifications is a list of dicts. Example:
		     [{'name': 'foo', 'vcs': 'bar', 'enabled': True},
		      {'name': 'baz', 'vcs': 'quux', 'enabled': False}]
		"""
		for n in notifications:
			if not session_user.is_admin:
				if not repository.userHasReadPermissions(self._name,
						n['name'], n['vcs']):
					raise UserPermissionError(
						'User %s has no read permission on %s (%s)' %
						(self._name, n['name'], n['vcs']))

		# if no Exception was thrown, set all notifications
		for n in notifications:
			storage.set_notification(self._id,
				n['name'], n['vcs'], n['enabled'],
				commit=False)

		# This will speed up the database process if there are many notifications
		# to save (users * repositories).
		storage.commit()
		trigger_hook('user-notifications-update', username=self._name)

	def notifications(self):
		"""Returns a dict of dicts, in the following layout:
		{
			'reposname1': {'vcs': 'git', 'enabled': False},
			'repos2': {'vcs': 'svn', 'enabled': True}
		}
		"""
		from submin.models.permissions import list_by_user
		notifications = {}
		for perms in list_by_user(self._name):
			reposname = perms['repository']
			if reposname in notifications:
				continue

			if not perms['permission'] in ('r', 'rw'):
				continue

			notification = {
				'vcs': perms['vcs'],
				'enabled': storage.notification(self._id, reposname, perms['vcs'])
			}
			notifications[perms['repository']] = notification

		return notifications

	def ssh_keys(self):
		"""Returns a list of tuples, containing the title and public key of
		each stored SSH key"""
		return storage.ssh_keys(self._id)

	def add_ssh_key(self, ssh_key, title=None):
		if title is None:
			title = ssh_key.strip().split()[-1]

		if not validators.validate_ssh_key(ssh_key):
			raise validators.InvalidSSHKey(ssh_key)

		storage.add_ssh_key(self._id, ssh_key, title)
		trigger_hook('user-update', username=self._name)

	def remove_ssh_key(self, ssh_key_id):
		storage.remove_ssh_key(ssh_key_id)
		trigger_hook('user-update', username=self._name)

	# Properties
	def _getId(self):
		return self._id

	def _getName(self):
		return self._name

	def _setName(self, name):
		if not validators.validate_username(name):
			raise validators.InvalidUsername(name)
		oldname = self._name
		self._name = name
		storage.set_name(self._id, name)
		trigger_hook('user-update', username=self._name, user_oldname=oldname)

	def _getEmail(self):
		return self._email

	def _setEmail(self, email):
		self._email = email
		if not validators.validate_email(email):
			raise validators.InvalidEmail(email)
		storage.set_email(self._id, email)

	def _getFullname(self):
		return self._fullname

	def _setFullname(self, fullname):
		self._fullname = fullname
		if not validators.validate_fullname(fullname):
			raise validators.InvalidFullname(fullname)
		storage.set_fullname(self._id, fullname)

	def _getIsAdmin(self):
		return self._is_admin

	def _setIsAdmin(self, is_admin):
		self._is_admin = is_admin
		storage.set_is_admin(self._id, is_admin)

	id       = property(_getId)   # id is read-only
	name     = property(_getName,     _setName)
	email    = property(_getEmail,    _setEmail)
	fullname = property(_getFullname, _setFullname)
	is_admin = property(_getIsAdmin,  _setIsAdmin)

__doc__ = """
Storage contract
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
	Sets the password for a user with userid *id* to *password*, in storage's
	native format.

* get_password_hash(id)
	Gets the password hash for a user with userid *id* from storage. Please use
	this wisely and minimise exposing these hashes. They are useful for
	exporting to an htpasswd-file for example.

* set_md5_password(id, password)
	Sets the md5 password for a user with userid *id* to *password*. If this is
	not supported by the module, it raises an MD5NotSupported error. This
	method is mainly used to convert htpasswd files to storage plugins that
	also use md5 to encrypt passwords.

* valid_password_reset_key(userid)
	Check if the key is valid and not expired for this user.

* set_password_reset_key(userid, key)
	Prepare the password reset, returns a special key that the user must
	present to reset the password. This key can be mailed to the user, for
	example. This overwrites any previous keys _for that user_.

* clear_password_reset_key(userid)
	Clear password reset key, for example when a user has reset her password.

* remove(userid)
	Removes user with id *userid*. Before a user can be removed, all
	remove_-functions below must have been called. This happens in the model,
	so storage plugin designers need not worry about this restriction.

* remove_from_groups(userid)
	Removes user with id *userid* from groups

* remove_permissions_repository(userid)
	Removes a user's repository permissions

* remove_permissions_submin(userid)
	Removes a user's submin permissions

* remove_notifications(userid)
	Removes a user's notifications

* remove_all_ssh_keys(userid)
	Removes a user's ssh_keys (all of them)

* member_of(userid)
	Returns sorted list of groups a user is member of.

* nonmember_of(userid)
	Returns sorted list of groups a user is not a member of.

* notification(userid, repository)
	Returns a dict of the notification, or None if it doesn't exist. The dict
	looks like: {'allowed': True, 'enabled': False}

* set_notification(userid, repository, vcstype, enabled)
	Set notification *enabled* (both booleans) for user *userid*
	on repository *repository* of type *vcstype*

* ssh_keys(userid)
	Returns a list of ssh_keys (dicts like
	{'id': id, 'title': title, 'key': key})

* add_ssh_key(userid, ssh_key, title)
	Adds an ssh key for user with id *userid*.

* remove_ssh_key(ssh_key_id)
	Removes a single ssh_key with id *ssh_key_id*.

* set_email(id, email)
	Sets the email for user with id *id*

* set_fullname(id, fullname)
	Sets the fullname for user with id *id*

* set_is_admin(id, is_admin)
	Sets whether user with id *id* is an admin
"""
