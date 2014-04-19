import os
import errno
import subprocess

from submin.models import options
from submin.models.exceptions import MissingConfig
from submin.common.execute import check_output
from submin.common.osutils import mkdirs

class TracAdminError(Exception):
	def __init__(self, cmd, exitstatus, outtext):
		self.cmd = cmd
		self.exitstatus = exitstatus
		self.outtext = outtext
		Exception.__init__(self,
				"trac-admin '%s' exited with exit status %d. Output from the command: %s" % \
				(cmd, exitstatus, outtext))

# trac components to enable for each vcs type
_trac_vcs_components = {
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


def create(vcs_type, reposname, adminUser):
	from submin.models.repository import directory as repodir
	basedir = options.env_path('trac_dir')
	mkdirs(str(basedir))

	tracenv = basedir + reposname
	projectname = reposname
	vcsdir = repodir(vcs_type, reposname)

	admin_command(tracenv,
			['initenv', projectname, 'sqlite:db/trac.db', vcs_type, vcsdir])
	admin_command(tracenv, ['permission', 'add', adminUser.name, "TRAC_ADMIN"])

	components = [
		'tracopt.ticket.commit_updater.committicketreferencemacro',
		'tracopt.ticket.commit_updater.committicketupdater',
	]

	components.extend(_trac_vcs_components[vcs_type])

	for component in components:
		admin_command(tracenv,
			['config', 'set', 'components', component, 'enabled'])

def admin_command(trac_dir, args):
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

def has_trac_admin():
	try:
		admin_command('/tmp', ['help'])
	except OSError, e:
		if e.errno == errno.ENOENT: # could not find executable
			return False
		raise

	return True

def exists(name):
	try:
		return os.path.isdir(str(options.env_path('trac_dir') + name))
	except UnknownKeyError, e:
		raise MissingConfig('Please make sure "trac_dir" is set in the config')
