import os

def create_dir(env, directory):
	"""Create a relative or absulute directory, if it doesn't exist already.
	Requires `env` to be a Path object."""
	if not directory.absolute:
		directory = env + directory

	if not os.path.exists(str(directory)):
		try:
			os.makedirs(str(directory), mode=0700)
		except OSError, e:
			print 'making dir %s failed, do you have permissions?' % \
					str(directory)
			raise e
