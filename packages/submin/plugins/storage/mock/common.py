
def database_evolve():
	pass

def database_backup():
	pass

def database_isuptodate():
	return True

def close():
	from user import clear_users
	from group import clear_groups
	from options import clear_options
	clear_users()
	clear_groups()
	clear_options()

def open(settings):
	pass

def setup():
	pass
