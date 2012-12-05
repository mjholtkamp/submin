import errno
from submin.models import trac

def trac_admin_command(trac_dir, args):
	try:
		trac.trac_admin_command(trac_dir, args)
	except TracAdminError, e:
		print "Trac command '%s' failed with exitcode %s" % (e.cmd, e.exitstatus)
		print 'Error message:'
		print e.outtext
		raise

def deploy(trac_dir, deploy_dir):
	trac_admin_command(trac_dir, ['deploy', deploy_dir])

def exists():
	return trac.exists()

def initenv(trac_dir, trac_name):
	trac_admin_command(trac_dir, ['initenv', trac_name, 'sqlite:db/trac.db'])
