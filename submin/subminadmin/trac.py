import subprocess
import errno

def trac_admin_command(trac_dir, args):
	"""trac_dir is the trac env dir, args is a list of arguments to trac-admin"""
	cmd = ['trac-admin', trac_dir]
	cmd.extend(args)

	try:
		subprocess.check_output(cmd, stderr=subprocess.STDOUT)
	except subprocess.CalledProcessError, e:
		print 'Trac command failed: ', ' '.join(cmd)
		print 'Error message:'
		print e.output
		raise

def deploy(trac_dir, deploy_dir):
	trac_admin_command(trac_dir, ['deploy', deploy_dir])

def exists():
	try:
		trac_admin_command('/tmp', ['help'])
	except OSError, e:
		if e.errno == errno.ENOENT: # could not find executable
			return False
		raise

	return True

def initenv(trac_dir, trac_name):
	trac_admin_command(trac_dir, ['initenv', trac_name, 'sqlite:db/trac.db'])
