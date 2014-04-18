import os
import sys
import commands
import errno

from submin.models import options, repository
from submin.template.shortcuts import evaluate
from submin.common.osutils import mkdirs
from common import set_git_config, SetGitConfigError
from common import rewrite_hook, signature
from submin.common import shellscript

HOOK_VERSIONS = {
	'commit-email': 5,
	'trac-sync': 5,
}

def prepare(reponame):
	"""Make sure basic things are in place for post-receive scripts to work.
	The post-receive hook calls hook-mux, which multiplexes everything on
	standard input to multiple scripts found in the post-recieve.d directory.

	This makes it possible to have multiple (post-receive) hooks.
	"""
	hook_dir = repository.directory('git', reponame) + 'hooks'

	# Make sure multiplexer script is in place. It should be a shell script
	# that calls the actual real script. The old situation is that the
	# post-receive script was actually a script to call only git-multimail.py.
	# The reason why we have a call to the script instead of a symlink, is
	# because we can not guarantee the executable bit of the target.
	if not shellscript.hasSignature(hook_dir + 'post-receive', signature):
		rewrite_hook(reponame, 'post-receive', 'hook-mux',
			interpreter='/bin/bash', args='post-receive')

	# make sure multiplexer dir exists
	# because www user can check if files in this directory exists, but
	# we can't chgrp() the dir, we set the mode explicitly to 0755. The
	# parent dir is only open to git user and www group, with mode 0750.
	mkdirs(hook_dir + 'post-receive.d', mode=0755)

def setCommitEmailHook(reponame, enable):
	prepare(reponame)

	reposdir = repository.directory('git', reponame)
	hook_dir = reposdir + 'hooks' + 'post-receive.d'
	mkdirs(hook_dir)
	hook_dest = hook_dir + '001-commit-email.hook'

	if enable:
		variables = {
			'submin_lib_dir': options.lib_path(),
			'base_url': options.url_path('base_url_submin'),
			'http_vhost': options.http_vhost(),
			'hook_version': HOOK_VERSIONS['commit-email'],
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
			cfg = repository.directory('git', reponame) + 'config'
			email = options.value('commit_email_from',
				'Please configure commit_email_from <noreply@example.net>')

			set_git_config(cfg, 'multimailhook.emailmaxlines', '2000')
			prefix = '[%s]' % reponame
			set_git_config(cfg, 'multimailhook.emailprefix', prefix)
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

	hook_dir = repository.directory('git', reponame) + 'hooks'
	hook = hook_dir + 'post-receive.d' + '002-trac-sync.hook'

	try:
		os.unlink(hook)
	except OSError, e:
		if e.errno != errno.ENOENT:
			raise repository.PermissionError(
				"Removing trac-sync hook failed: %s" % (str(e),))

	if not enable:
		return

	variables = {
		'submin_env': str(options.env_path()),
		'repository': reponame,
		'hook_version': HOOK_VERSIONS['trac-sync'],
	}
	contents = evaluate('plugins/vcs/git/trac-sync', variables)
	with file(hook, 'w') as f:
		f.writelines(contents)

	os.chmod(hook, 0755)

def rewrite_hooks(reponame):
	if reponame:
		repositories = [reponame]
	else:
		repositories = [x['name'] for x in repository.Repository.list_all() if x['vcs'] == 'git']

	for reponame in repositories:
		repo = repository.Repository(reponame, 'git')

		setCommitEmailHook(reponame, repo.commitEmailsEnabled())
		setTracSyncHook(reponame, repo.tracCommitHookEnabled())
