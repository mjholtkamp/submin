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
	except subprocess.CalledProcessError as e:
		if e.returncode != 5: # unset an option that doesn't exist
			raise SetGitConfigError(str(e))

def rewrite_hook(reponame, hookname, targetname,
			interpreter='/usr/bin/python', args='"$@"'):
	if reponame:
		repositories = [reponame]
	else:
		repositories = [x['name'] for x in repository.Repository.list_all() if x['vcs'] == 'git']
	for reponame in repositories:
		reposdir = repository.directory('git', reponame)
		backup_old_hook(reposdir, hookname)
		enable_hook(reposdir, hookname, targetname, interpreter, args)

def backup_old_hook(reposdir, hookname):
	hook = reposdir + 'hooks' + hookname
	try:
		os.rename(hook, str(hook) + '.submin2.backup')
	except OSError as e:
		if e.errno != errno.ENOENT:
			raise

def enable_hook(reposdir, hookname, targetname,
			interpreter='/usr/bin/python', args='"$@"'):
	"""Assumes no hook is already there, or if there is, that is a shell script.
	If you want to overwrite the hook with a clean submin-hook, call rewrite_hook instead."""
	target_script = options.static_path("hooks") + "git" + targetname
	new_hook = '%s %s %s\n' % (interpreter, target_script, args)
	hook = reposdir + 'hooks' + hookname

	if shellscript.hasSignature(hook, signature):
		return

	shellscript.rewriteWithSignature(hook, signature, new_hook, True, mode=0o755)

