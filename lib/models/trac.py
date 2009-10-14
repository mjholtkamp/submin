import exceptions
import commands
import os
from models.options import Options
from models.exceptions import UnknownKeyError

class UnknownTrac(Exception):
	def __init__(self, name):
		Exception.__init__(self, "Could not find trac env '%s'" % name)

class MissingConfig(Exception):
	pass

def tracBaseDir():
	o = Options()
	try:
		basedir = o.env_path('trac_dir')
	except UnknownKeyError:
		raise MissingConfig('No Trac directory specified in options')

	return basedir

def createTracEnv(repository):
	o = Options()
	basedir = tracBaseDir()
	if not os.path.isdir(str(basedir)):
		os.makedirs(str(basedir))

	tracenv = basedir + repository
	projectname = repository
	svnbasedir = o.env_path('svn_dir')
	svndir = svnbasedir + repository
	try:
		path = o.value('path')
	except UnknownKeyError:
		path = "/bin:/usr/bin:/usr/local/bin:/opt/local/bin"

	cmd =  "PATH='%s' trac-admin '%s' initenv '%s' 'sqlite:db/trac.db' 'svn' '%s'" % \
		(path, tracenv, projectname, svndir)
	(exitstatus, outtext) = commands.getstatusoutput(cmd)
	return (exitstatus == 0, outtext)

class Trac(object):
	def __init__(self, name):
		self.name = name
		self.basedir = tracBaseDir()

		tracenv = str(self.basedir + self.name)
		if not os.path.isdir(tracenv):
			raise UnknownTrac(tracenv)
