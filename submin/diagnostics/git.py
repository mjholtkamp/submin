import os
import re
import errno

from submin.models import options
from submin.models.exceptions import UnknownKeyError
from submin.plugins.vcs.git import remote
from submin.subminadmin.git.post_receive_hook import HOOK_VERSIONS
from submin.common import shellscript

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

	try:
		git_ssh_host = options.value('git_ssh_host')
	except UnknownKeyError:
		results['git_hostname_ok'] = False
	else:
		results['git_hostname_ok'] = True
		if git_ssh_host in ('localhost', '127.0.0.1', '::1'):
			results['git_hostname_ok'] = False

	try:
		remote.execute("update-auth")
	except (remote.NonZeroExitStatus, UnknownKeyError), e:
		results['git_admin_test'] = False
		results['git_admin_test_errmsg'] = str(e)
	else:
		results['git_admin_test'] = True

	results['git_all'] = False not in results.values()
	
	return results

def hook_uptodate(filename, version_re, newest_version):
	"""For hooks that are generated from a template, they may be out of
	date if the template is newer than the generated template. The version_re
	is a regular expression with one capture group (the version as a number)"""
	try:
		hook = file(filename, 'r').readlines()
	except IOError, e:
		if e.errno == errno.ENOENT:
			return False

	versions = re.findall(version_re, "\n".join(hook))
	if len(versions) != 1:
		return False

	if int(versions[0]) < newest_version:
		return False

	return True

def old_hook_dirs(git_dir_root):
	signature = '### SUBMIN GIT AUTOCONFIG, DO NOT ALTER FOLLOWING LINE ###\n'
	git_dirs = []
	for root, dirs, files in os.walk(git_dir_root):
		for d in dirs:
			if d.endswith('.git'):
				git_dirs.append(d)
		break

	for git_dir in sorted(git_dirs):
		# check update hook
		filename = os.path.join(git_dir_root, git_dir, 'hooks', 'update')
		if not shellscript.hasSignature(filename, signature):
			yield git_dir
			continue # no need to check other hooks

		# check multiplexer script
		filename = os.path.join(git_dir_root, git_dir, 'hooks', 'post-receive')
		if not os.path.exists(filename):
			yield git_dir
			continue

		# ok, it exists, but does it point to the right place?
		hook_to = options.static_path('hooks') + 'git' + 'hook-mux'
		target = None
		try:
			target = os.readlink(filename)
		except OSError, e:
			if e.errno != errno.EINVAL:
				raise

		if target != hook_to:
			yield git_dir
			continue

		# check commit-email hook
		filename = os.path.join(git_dir_root, git_dir, 'hooks',
				'post-receive.d', '001-commit-email.hook')
		# no post-receive hook = no commit emails enabled
		if os.path.exists(filename):
			if not hook_uptodate(filename, 'HOOK_VERSION = (\d+)',
					HOOK_VERSIONS['commit-email']):
				yield git_dir

		# check trac-sync hook
		filename = os.path.join(git_dir_root, git_dir, 'hooks',
				'post-receive.d', '002-trac-sync.hook')
		# no post-receive hook = no trac-sync enabled
		if os.path.exists(filename):
			if not hook_uptodate(filename, 'HOOK_VERSION=(\d+)',
					HOOK_VERSIONS['trac-sync']):
				yield git_dir


	return

