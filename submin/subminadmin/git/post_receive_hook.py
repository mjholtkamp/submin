import os
import sys
import commands
import errno

from submin.models import options, repository
from submin.template.shortcuts import evaluate
from submin.common.osutils import mkdirs
from common import set_git_config, SetGitConfigError

HOOK_VERSION = 3

def prepare(reponame):
	"""Make sure basic things are in place for post-receive scripts to work.
	For the post-receive-hook, we put a symlink to the hook-mux script, which
	multiplexes everything on standard input to multiple scripts found in the
	post-recieve.d directory.

	This makes it possible to have multiple (post-receive) hooks.
	"""
	if not reponame.endswith(".git"):
		reponame += ".git"

	# make sure multiplexer script is in place (symlink to 'hook-mux')
	hook_dir = options.env_path('git_dir') + reponame + 'hooks'
	hook_from = hook_dir + 'post-receive'
	hook_to = options.static_path('hooks') + 'git' + 'hook-mux'
	target = None
	try:
		target = os.readlink(hook_from)
	except OSError, e:
		if not e.errno in (errno.EINVAL, errno.ENOENT):
			raise

	# fix symlink, if necessary
	if target != hook_to:
		try:
			os.rename(hook_from, str(hook_from) + '.submin2.backup')
		except OSError, e:
			if e.errno != errno.ENOENT:
				raise
		os.symlink(hook_to, hook_from)

	# make sure multiplexer dir exists
	# because www user can check if files in this directory exists, but
	# we can't chgrp() the dir, we set the mode explicitly to 0755. The
	# parent dir is only open to git user and www group, with mode 0750.
	mkdirs(hook_dir + 'post-receive.d', mode=0755)

def setCommitEmailHook(reponame, enable):
	if not reponame.endswith(".git"):
		reponame += ".git"

	prepare(reponame)

	reposdir = options.env_path('git_dir') + reponame
	hook_dir = reposdir + 'hooks' + 'post-receive.d'
	mkdirs(hook_dir)
	hook_dest = hook_dir + '001-commit-email.hook'

	if enable:
		variables = {
			'submin_lib_dir': options.lib_path(),
			'base_url': options.url_path('base_url_submin'),
			'http_vhost': options.http_vhost(),
			'hook_version': HOOK_VERSION,
		}
		hook = evaluate('plugins/vcs/git/post-receive', variables)
		try:
			os.unlink(hook_dest)
		except OSError, e:
			if e.errno != errno.ENOENT:
				raise

		try:
			with file(hook_dest, 'w') as f:
				f.write(hook)

			os.chmod(hook_dest, 0755)
		except OSError, e:
			raise repository.PermissionError(
				"Enabling hook failed: %s" % (str(e),))
		try:
			cfg = options.env_path('git_dir') + reponame + 'config'
			email = options.value('commit_email_from', 'Please configure commit_email_from <noreply@example.net>')
			set_git_config(cfg, 'multimailhook.emailmaxlines', '2000')
			set_git_config(cfg, 'multimailhook.emailprefix', '[Submin]')
			set_git_config(cfg, 'multimailhook.envelopesender', email)
		except SetGitConfigError, e:
			raise repository.PermissionError(
				"Enabling hook succeeded, but configuring it failed: %s" %
				(str(e)))
	else:
		try:
			os.unlink(hook_dest)
		except OSError, e:
			if e.errno != errno.ENOENT:
				raise repository.PermissionError(
					"Removing hook failed: %s" % (str(e),))

def setTracSyncHook(reponame, enable):
	prepare(reponame)

def rewrite_hook(reponame):
	if reponame:
		repositories = [reponame]
	else:
		repositories = [x['name'] for x in repository.Repository.list_all() if x['vcs'] == 'git']

	for reponame in repositories:
		repo = repository.Repository(reponame, 'git')

		setCommitEmailHook(reponame, repo.commitEmailsEnabled())
		setTracSyncHook(reponame, repo.tracCommitHookEnabled())
