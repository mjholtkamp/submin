import os
import sys
import errno
import commands
import shutil

from submin.common import shellscript
from submin.models import options, repository

def run(reponame):
	reposdir = _git_dirname(reponame)

	old_path = os.environ["PATH"]
	os.environ["PATH"] = options.value("env_path")
	cmd = 'GIT_DIR="%s" git --bare init' % str(reposdir)
	(exitstatus, outtext) = commands.getstatusoutput(cmd)
	os.environ["PATH"] = old_path

	_enable_hook(reposdir)

	if exitstatus != 0:
		raise PermissionError(
			"External command 'GIT_DIR=\"%s\" git --bare init' failed: %s" % \
					(name, outtext))

def rewrite_hook(reponame):
	if reponame:
		repositories = [reponame]
	else:
		repositories = [x['name'] for x in repository.Repository.list_all() if x['vcs'] == 'git']
	for reponame in repositories:
		reposdir = _git_dirname(reponame)
		hook = reposdir + 'hooks' + 'update'
		try:
			os.rename(hook, str(hook) + '.submin2.backup')
		except OSError, e:
			if e.errno != errno.ENOENT:
				raise
		_enable_hook(reposdir)

def _enable_hook(reposdir):
	"""Assumes no hook is already there, or if there is, that is a shell script.
	If you want to overwrite the hook with a clean submin-hook, call rewrite_hook instead."""
	signature = "### SUBMIN GIT AUTOCONFIG, DO NOT ALTER FOLLOWING LINE ###\n"
	target_script = options.static_path("hooks") + "git" + "update"
	new_hook = '/usr/bin/python %s "$@"\n' % (target_script, )
	hook = reposdir + 'hooks' + 'update'

	shellscript.rewriteWithSignature(hook, signature, new_hook, True, mode=0755)

def _git_dirname(reponame):
	if not reponame.endswith('.git'):
		reponame += '.git'
	return options.env_path('git_dir') + reponame

