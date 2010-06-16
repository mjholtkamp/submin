import commands

from submin.models import options

class NonZeroExitStatus(Exception):
	pass

def execute(remote_command):
	ssh_key_path = options.env_path() + 'conf' + 'id_dsa'

	# The options provided with the -o flags are to prevent ssh trying to
	# create a '.ssh' directory in the homedir of the www user.
	cmd = 'ssh -i "%s" %s@%s -p %s -o "StrictHostKeyChecking=no"'
	cmd += ' -o "UserKnownHostsFile=/dev/null" %s'
	(exitstatus, outtext) = commands.getstatusoutput(cmd % (ssh_key_path,
		options.value("git_user"), options.value("git_ssh_host"),
		options.value("git_ssh_port"), remote_command))

	if exitstatus != 0:
		raise NonZeroExitStatus(outtext)
