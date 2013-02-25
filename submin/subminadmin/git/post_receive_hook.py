import os
import sys
import commands

from submin.models import options, repository
from submin.template.shortcuts import evaluate
from common import set_git_config, SetGitConfigError

def run(reponame, enable=True):
	if not reponame.endswith(".git"):
		reponame += ".git"

	reposdir = options.env_path('git_dir') + reponame
	hook_dest = reposdir + 'hooks' + 'post-receive'

	if enable:
		variables = {
			'submin_lib_dir': options.lib_path(),
			'base_url': options.url_path('base_url_submin'),
			'http_vhost': options.url_path('http_vhost'),
		}
		hook = evaluate('plugins/vcs/git/post-receive', variables)
		try:
			os.rename(hook_dest, str(hook_dest) + '.submin2.org')
		except OSError, e:
			# maybe file didn't exist... oh well
			# if it's something else, we will raise an exception when
			# writing the file anyway
			pass 

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
			os.rename(hook_dest, str(hook_dest) + '.submin2.disabled')
		except OSError, e:
			raise repository.PermissionError(
				"Renaming hook failed: %s" % (str(e),))

def rewrite_hook(reponame):
	if reponame:
		repositories = [reponame]
	else:
		repositories = [x['name'] for x in repository.Repository.list_all() if x['vcs'] == 'git']

	for reponame in repositories:
		enabled = repository.Repository(reponame, 'git').commitEmailsEnabled()
		# no need to disable if not enabled
		if enabled:
			run(reponame, enabled)
