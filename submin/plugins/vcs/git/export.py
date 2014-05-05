from submin.plugins.vcs.git import remote
from submin.models import repository

def export_ssh_keys(*args, **kwargs):
	try:
		remote.execute("update-auth")
	except remote.NonZeroExitStatus as e:
		raise Exception("Could not export ssh-keys: %s" % e)

def export_notifications(**args):
	repositories = ""
	if 'reposname' in args.iterkeys():
		repositories = args['reposname']

	try:
		remote.execute("update-notifications %s" % (repositories,))
	except remote.NonZeroExitStatus as e:
		raise Exception("Could not update notifications: %s" % e)
