from submin.models.exceptions import UserExistsError

mock_users = [] # [{'id': 0, 'name': 'test'}]
mock_notifications = {} # {'reposname': {'allowed': True, 'enabled': False}}

def clear_users():
	global mock_users
	mock_users = []

def id2name(userid):
	return mock_users[userid]["name"]

def list():
	"""Generator for sorted list of users"""
	return mock_users

def add(username, password):
	for user in mock_users:
		if user['name'] == username:
			raise UserExistsError("User `%s' already exists" % username)

	mock_users.append({'name': username, 'password': password, 'email': '',
		'fullname': username, 'is_admin': False})
	u = mock_users[-1]
	u['id'] = mock_users.index(u)

def check_password(userid, password):
	return mock_users[userid]['password'] == password

def set_password(userid, password):
	mock_users[userid]['password'] = password

# Remove functions, removes users from various tables
def remove_from_groups(userid):
	pass

def remove_permissions_repository(userid):
	pass

def remove_permissions_submin(userid):
	pass

def remove_notifications(userid):
	global mock_notifications
	mock_notifications = {}

def remove_all_ssh_keys(userid):
	pass

def notification(userid, repository):
	global mock_notifications
	if not mock_notifications.has_key(repository):
		return None
	return mock_notifications[repository]

def set_notification(userid, repository, allowed, enabled):
	global mock_notifications
	mock_notifications[repository] = {'allowed': allowed, 'enabled': enabled}

def remove(userid):
	del mock_users[userid]

def ssh_keys(userid):
	pass

def add_ssh_key(userid, ssh_key, title):
	pass

def remove_ssh_key(ssh_key_id):
	pass

def user_data(username):
	for user in mock_users:
		if user['name'] == username:
			return user

	return None

def field_setter(field):
	def set_field(userid, value):
		mock_users[userid][field] = value
	return set_field

set_name     = field_setter("name")
set_email    = field_setter("email")
set_fullname = field_setter("fullname")
set_is_admin = field_setter("is_admin")

def member_of(userid):
	pass

def nonmember_of(userid):
	pass
