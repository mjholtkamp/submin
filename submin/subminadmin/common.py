import os
import commands

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

class SubminAdminCmdException(Exception):
	pass

class CmdException(Exception):
	def __init__(self, usermsg, errormsg, cmd):
		Exception.__init__(self, "%s: %s (%s)" % (usermsg, errormsg, cmd))
		self.usermsg = usermsg
		self.errormsg = errormsg
		self.cmd = cmd

def executeCmd(cmd, usermsg=""):
	(exitstatus, outtext) = commands.getstatusoutput(cmd)
	if exitstatus != 0:
		raise CmdException(usermsg, outtext, cmd)

def which(program):
	from submin.models import options

	def is_exe(fpath):
		return os.path.exists(fpath) and os.access(fpath, os.X_OK)

	env_path = options.value("env_path")
	for path in env_path.split(os.pathsep):
		prog_path = os.path.join(path, program)
		if is_exe(prog_path) and os.path.isfile(prog_path):
			return prog_path

	raise ProgramNotFoundError(program, env_path)


def www_user(preferred=''):
	"""Returns pwnam entry of most probably www-user"""
	from pwd import getpwnam
	users = []
	known = [preferred, 'www-data', 'httpd', 'apache', '_www', 'wwwrun', 'www']
	for user in known:
		pwd = ()
		try:
			pwd = getpwnam(user)
		except KeyError, e:
			pass
		else:
			return pwd

