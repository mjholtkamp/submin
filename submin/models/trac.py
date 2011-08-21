import exceptions
import commands
import os
from submin.models import options
from submin.models.exceptions import UnknownKeyError

class UnknownTrac(Exception):
	def __init__(self, name):
		Exception.__init__(self, "Could not find trac env '%s'" % name)

class MissingConfig(Exception):
	pass

class TracAdminError(Exception):
	def __init__(self, exitstatus, outtext):
		Exception.__init__(self,
				"trac-admin exited with exit status %d. Output from the command: %s" % (exitstatus, outtext))

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
	path = options.value('env_path', "/bin:/usr/bin:/usr/local/bin:/opt/local/bin")

	cmd =  "PATH='%s' trac-admin '%s' initenv '%s' 'sqlite:db/trac.db' 'svn' '%s'" % \
		(path, tracenv, projectname, svndir)
	(exitstatus, outtext) = commands.getstatusoutput(cmd)
	if exitstatus != 0:
		raise TracAdminError(exitstatus, outtext)

	cmd = "PATH='%s' trac-admin '%s' permission add '%s' TRAC_ADMIN" % \
			(path, tracenv, adminUser.name)
	(exitstatus, outtext) = commands.getstatusoutput(cmd)
	if exitstatus != 0:
		raise TracAdminError(exitstatus, outtext)

class Trac(object):
	def __init__(self, name):
		self.name = name
		self.basedir = tracBaseDir()

		tracenv = str(self.basedir + self.name)
		if not os.path.isdir(tracenv):
			raise UnknownTrac(tracenv)
