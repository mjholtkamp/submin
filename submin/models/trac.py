import exceptions
import subprocess
import os
import errno
from submin.models import options
from submin.models.exceptions import UnknownKeyError
from submin.common.execute import check_output

class UnknownTrac(Exception):
	def __init__(self, name):
		Exception.__init__(self, "Could not find trac env '%s'" % name)

class MissingConfig(Exception):
	pass

class TracAdminError(Exception):
	def __init__(self, cmd, exitstatus, outtext):
		self.cmd = cmd
		self.exitstatus = exitstatus
		self.outtext = outtext
		Exception.__init__(self,
				"trac-admin '%s' exited with exit status %d. Output from the command: %s" % \
				(cmd, exitstatus, outtext))

def tracBaseDir():
	try:
		basedir = options.env_path('trac_dir')
	except UnknownKeyError:
		raise MissingConfig('No Trac directory specified in options')

	return basedir

def createTracEnv(repository, adminUser):
	basedir = tracBaseDir()
	if not os.path.isdir(str(basedir)):
		os.makedirs(str(basedir))

	tracenv = basedir + repository
	projectname = repository
	svnbasedir = options.env_path('svn_dir')
	svndir = svnbasedir + repository

	trac_admin_command(tracenv, ['initenv', projectname, 'sqlite:db/trac.db', 'svn', svndir])
	trac_admin_command(tracenv, ['permission', 'add', adminUser.name, "TRAC_ADMIN"])

def trac_admin_command(trac_dir, args):
	"""trac_dir is the trac env dir, args is a list of arguments to trac-admin"""
	cmd = ['trac-admin', trac_dir]
	cmd.extend(args)
	path = options.value('env_path', "/bin:/usr/bin:/usr/local/bin:/opt/local/bin")
	env_copy = os.environ.copy()
	env_copy['PATH'] = path

	try:
		return check_output(cmd, stderr=subprocess.STDOUT, env=env_copy)
	except subprocess.CalledProcessError, e:
		raise TracAdminError(' '.join(cmd), e.returncode, e.output)

def tracAdminExists():
	try:
		trac_admin_command('/tmp', ['help'])
	except OSError, e:
		if e.errno == errno.ENOENT: # could not find executable
			return False
		raise

	return True

class Trac(object):
	def __init__(self, name):
		self.name = name
		self.basedir = tracBaseDir()

		tracenv = str(self.basedir + self.name)
		if not os.path.isdir(tracenv):
			raise UnknownTrac(tracenv)
