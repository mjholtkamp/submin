import subprocess

class SetGitConfigError(Exception):
	pass

def set_git_config(configfile, key, val):
	cmd = ["git", "config", "-f", configfile]
	if val is None:
		cmd.extend(["--unset", key])
	else:
		cmd.extend([key, val])
		
	try:
		subprocess.check_call(cmd)
	except subprocess.CalledProcessError, e:
		if e.returncode != 5: # unset an option that doesn't exist
			raise SetGitConfigError(str(e))
