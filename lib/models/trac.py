from ConfigParser import NoOptionError, NoSectionError
from config.config import Config
import exceptions
import commands
import os

class UnknownTrac(Exception):
	def __init__(self, name):
		Exception.__init__(self, "Could not find trac env '%s'" % name)

class MissingConfig(Exception):
	def __init__(self, msg):
		Exception.__init__(self, '%s' % msg)

def tracBaseDir():
	config = Config()
	try:
		basedir = config.getpath('trac', 'basedir')
		return basedir
	except (NoOptionError, NoSectionError):
		raise MissingConfig("No 'basedir' in [trac] section")

def createTracEnv(repository):
	config = Config()
	basedir = tracBaseDir()
	if not os.path.isdir(str(basedir)):
		os.makedirs(str(basedir))

	tracenv = basedir + repository
	projectname = repository
	svnbasedir = config.getpath('svn', 'repositories')
	svndir = svnbasedir + repository
	try:
		path = config.get('backend', 'path')
	except NoOptionError:
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
