mock_users = [] # [{'id': 0, 'name': 'test'}]
mock_groups = {} # {"mock": {'id': 0, 'name': 'mock', 'members': []}}

def teardown():
	# Because `from __init__ import mock_users' makes a copy of the list, we
	# cannot simply delete the users from this list, we have to ask the
	# user-module to perform this action for us
	# XXX: Isn't it better to move mock_users back to the users module then?
	from user import clear_users
	from group import clear_groups
	clear_users()
	clear_groups()

def init(settings):
	pass

def setup():
	pass
