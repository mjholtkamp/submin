import exceptions
import subprocess
import os
import errno
from submin.models import options
from submin.models.exceptions import UnknownKeyError
from submin.common.execute import check_output
from submin.common.osutils import mkdirs

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

# trac components to enable for each vcs type
trac_vcs_components = {
	'git': [
		'tracopt.versioncontrol.git.git_fs.csetpropertyrenderer',
		'tracopt.versioncontrol.git.git_fs.gitconnector',
		'tracopt.versioncontrol.git.git_fs.gitwebprojectsrepositoryprovider'
	],
	'svn': [
		'tracopt.versioncontrol.svn.svn_fs.subversionconnector',
		'tracopt.versioncontrol.svn.svn_prop.subversionmergepropertydiffrenderer',
		'tracopt.versioncontrol.svn.svn_prop.subversionmergepropertyrenderer',
		'tracopt.versioncontrol.svn.svn_prop.subversionpropertyrenderer'
	]
}

def tracBaseDir():
	try:
		basedir = options.env_path('trac_dir')
	except UnknownKeyError:
		raise MissingConfig('No Trac directory specified in options')

	return basedir

def createTracEnv(vcs_type, reposname, adminUser):
	from submin.models.repository import directory as repodir
	basedir = tracBaseDir()
	mkdirs(str(basedir))

	tracenv = basedir + reposname
	projectname = reposname
	vcsdir = repodir(vcs_type, reposname)

	trac_admin_command(tracenv,
			['initenv', projectname, 'sqlite:db/trac.db', vcs_type, vcsdir])
	trac_admin_command(tracenv,
			['permission', 'add', adminUser.name, "TRAC_ADMIN"])

	components = [
		'tracopt.ticket.commit_updater.committicketreferencemacro',
		'tracopt.ticket.commit_updater.committicketupdater',
	]

	components.extend(trac_vcs_components[vcs_type])

	for component in components:
		trac_admin_command(tracenv,
			['config', 'set', 'components', component, 'enabled'])

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
