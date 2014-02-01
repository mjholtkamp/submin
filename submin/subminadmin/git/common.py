import os
import errno
import subprocess
from submin.models import options, repository
from submin.common import shellscript

signature = "### SUBMIN GIT AUTOCONFIG, DO NOT ALTER FOLLOWING LINE ###\n"

class SetGitConfigError(Exception):
	pass

def set_git_config(configfile, key, val):
	cmd = ["git", "config", "-f", configfile]
	if val is None:
		cmd.extend(["--unset", key])
	else:
		cmd.extend([key, val])
		
	try:
		subprocess.check_call(cmd)
	except subprocess.CalledProcessError, e:
		if e.returncode != 5: # unset an option that doesn't exist
			raise SetGitConfigError(str(e))

def rewrite_hook(reponame, hookname, targetname):
	if reponame:
		repositories = [reponame]
	else:
		repositories = [x['name'] for x in repository.Repository.list_all() if x['vcs'] == 'git']
	for reponame in repositories:
		reposdir = git_dirname(reponame)
		backup_old_hook(reposdir, hookname)
		enable_hook(reposdir, hookname, targetname)

def backup_old_hook(reposdir, hookname):
	hook = reposdir + 'hooks' + hookname
	try:
		os.rename(hook, str(hook) + '.submin2.backup')
	except OSError, e:
		if e.errno != errno.ENOENT:
			raise

def enable_hook(reposdir, hookname, targetname):
	"""Assumes no hook is already there, or if there is, that is a shell script.
	If you want to overwrite the hook with a clean submin-hook, call rewrite_hook instead."""
	target_script = options.static_path("hooks") + "git" + targetname
	new_hook = '/usr/bin/python %s "$@"\n' % (target_script, )
	hook = reposdir + 'hooks' + hookname

	if shellscript.hasSignature(hook, signature):
		return

	shellscript.rewriteWithSignature(hook, signature, new_hook, True, mode=0755)

def git_dirname(reponame):
	if not reponame.endswith('.git'):
		reponame += '.git'
	return options.env_path('git_dir') + reponame

