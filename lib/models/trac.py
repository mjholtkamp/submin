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
		basedir = config.get('trac', 'basedir')
		return basedir
	except (NoOptionError, NoSectionError):
		raise MissingConfig("No 'basedir' in [trac] section")

def createTracEnv(repository):
	config = Config()
	basedir = tracBaseDir()
	if not os.path.isdir(basedir):
		os.makedirs(basedir)

	tracenv = os.path.join(basedir, repository)
	projectname = repository
	svnbasedir = config.get('svn', 'repositories')
	svndir = os.path.join(svnbasedir, repository)
	path = config.get('backend', 'path')
	cmd =  "PATH=%s trac-admin %s initenv '%s' 'sqlite:db/trac.db' 'svn' '%s'" % \
		(path, tracenv, projectname, svndir)
	(exitstatus, outtext) = commands.getstatusoutput(cmd)
	return (exitstatus == 0, outtext)

class Trac(object):
	def __init__(self, name):
		self.name = name
		self.basedir = tracBaseDir()

		tracenv = os.path.join(self.basedir, self.name)
		if not os.path.isdir(tracenv):
			raise UnknownTrac(name)
