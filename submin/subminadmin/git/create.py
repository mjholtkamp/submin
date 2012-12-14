import os
import sys
import commands
import shutil

from submin.common import shellscript
from submin.models import options

def run(reponame):
	if not reponame.endswith(".git"):
		reponame += ".git"

	reposdir = options.env_path('git_dir') + reponame

	old_path = os.environ["PATH"]
	os.environ["PATH"] = options.value("env_path")
	cmd = 'GIT_DIR="%s" git --bare init' % str(reposdir)
	(exitstatus, outtext) = commands.getstatusoutput(cmd)
	os.environ["PATH"] = old_path

	# enable hook on creation
	signature = "### SUBMIN GIT AUTOCONFIG, DO NOT ALTER FOLLOWING LINE ###\n"
	target_script = options.static_path("hooks") + "git" + "update"
	new_hook = "/usr/bin/python %s\n" % (target_script, )
	hook = reposdir + "hooks" + "update"

	# touch new file, closes directly
	shellscript.rewriteWithSignature(hook, signature, new_hook, True, mode=0755)

	if exitstatus != 0:
		raise PermissionError(
			"External command 'GIT_DIR=\"%s\" git --bare init' failed: %s" % \
					(name, outtext))
