
def teardown():
	from user import clear_users
	from group import clear_groups
	from options import clear_options
	clear_users()
	clear_groups()
	clear_options()

def init(settings):
	pass

def setup():
	pass
