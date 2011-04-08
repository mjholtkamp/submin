from submin.plugins.vcs.git import remote

def export_ssh_keys(*args, **kwargs):
	try:
		remote.execute("update-auth")
	except remote.NonZeroExitStatus, e:
		raise Exception("Could not export ssh-keys: %s" % e)
