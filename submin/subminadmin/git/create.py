import os
import sys
import errno
import commands
import shutil

from submin.common import shellscript
from submin.models import options, repository

from .common import rewrite_hook
from . import post_receive_hook

def run(reponame):
	reposdir = repository.directory('git', reponame)

	old_path = os.environ["PATH"]
	os.environ["PATH"] = options.value("env_path")
	cmd = 'GIT_DIR="%s" git --bare init' % str(reposdir)
	(exitstatus, outtext) = commands.getstatusoutput(cmd)
	os.environ["PATH"] = old_path

	rewrite_hooks(reponame)
	post_receive_hook.rewrite_hooks(reponame)

	if exitstatus != 0:
		raise PermissionError(
			"External command 'GIT_DIR=\"%s\" git --bare init' failed: %s" % \
					(name, outtext))

def rewrite_hooks(reponame):
	rewrite_hook(reponame, 'update', 'update')

