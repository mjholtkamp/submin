import os

from submin.models import options
from submin.models import user
from submin.models.user import FakeAdminUser
from submin.models.exceptions import UnknownKeyError

def export_htpasswd(*args, **kwargs):
	try:
		htpasswd_file = options.env_path("htpasswd_file")
	except UnknownKeyError:
		return

	# XXX This should raise a flag in diagnostics, maybe?
	if not os.path.exists(htpasswd_file.dirname()):
		return

	with open(htpasswd_file, "w+") as htpasswd:
		for username in user.list(FakeAdminUser()):
			u = user.User(username)
			htpasswd.write("%s:%s\n" % (username, u.get_password_hash()))

