import os

from submin.models import options
from submin.models.exceptions import UnknownKeyError

def diagnostics():
	results = {}
	results['enabled_git'] = 'git' in options.value('vcs_plugins', '')

	try:
		git_dir = options.env_path('git_dir')
	except UnknownKeyError:
		results['git_dir_set'] = False
		results['git_hooks_all_new'] = True # because no repositories
		results['git_old_hook_repos'] = []
	else:
		results['git_dir_set'] = True
		old_dirs = list(old_hook_dirs(git_dir))
		results['git_hooks_all_new'] = len(old_dirs) == 0
		results['git_old_hook_repos'] = old_dirs

	results['git_all'] = False not in results.values()
	
	return results

def old_hook_dirs(git_dir_root):
	signature = '### SUBMIN GIT AUTOCONFIG, DO NOT ALTER FOLLOWING LINE ###\n'
	git_dirs = []
	for root, dirs, files in os.walk(git_dir_root):
		for d in dirs:
			if d.endswith('.git'):
				git_dirs.append(d)
		break

	for git_dir in git_dirs:
		hook = file(os.path.join(git_dir_root, git_dir, 'hooks', 'update'), 'r').readlines()
		if signature not in hook:
			yield git_dir
	return

