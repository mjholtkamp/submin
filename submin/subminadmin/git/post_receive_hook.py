import os
import sys
import commands

from submin.models import options
from submin.template.shortcuts import evaluate

def run(reponame, enable=True):
	if not reponame.endswith(".git"):
		reponame += ".git"

	reposdir = options.env_path('git_dir') + reponame
	hook_dest = reposdir + 'hooks' + 'post-receive'

	if enable:
		variables = {
			'submin_lib_dir': options.lib_path(),
			'submin_base_url': options.url_path('base_url_submin')
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
			raise PermissionError(
				"Enabling hook failed: %s" % (str(e),))
	else:
		try:
			os.rename(hook_dest, str(hook_dest) + '.submin2.disabled')
		except OSError, e:
			raise PermissionError(
				"Renaming hook failed: %s" % (str(e),))
