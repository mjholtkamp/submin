import os
import commands
import shutil
from submin.models import options

class c_trac():
	'''Trac support commands
Usage:
    trac init                      - (re)creates trac cgi/wsgi/fcgi scripts'''

	def __init__(self, sa, argv):
		self.sa = sa
		self.argv = argv

	def subcmd_init(self, argv):
		"""Initialize trac
		Why not just distribute them with submin? Two reasons: one is because
		they might change with each version of trac, two is because those scripts
		have a different license and IANAL so this is easier (reason one should
		be enough anyway).
		"""
		tmp_trac_dir = options.env_path() + 'tmp-trac'
		tmp_deploy_dir = tmp_trac_dir + 'deploy'

		# first, create a temp trac env, because 'deploy' needs a working trac
		# env (sigh)
		cmd = "trac-admin %s initenv dummy sqlite:db/trac.db" % (tmp_trac_dir)
		(exitstatus, outtext) = commands.getstatusoutput(cmd)
		if exitstatus > 0:
			print outtext

		# then generate the scripts
		cmd = "trac-admin %s deploy %s" % (tmp_trac_dir, tmp_deploy_dir)
		(exitstatus, outtext) = commands.getstatusoutput(cmd)
		if exitstatus > 0:
			print outtext

		# copy them to our cgi-bin
		cgi_bin_dir = options.env_path() + 'cgi-bin'
		for root, dirs, files in os.walk(str(tmp_deploy_dir + 'cgi-bin')):
			for filename in files:
				src = os.path.join(root, filename)
				dst = os.path.join(str(cgi_bin_dir), filename)
				os.rename(src, dst)
				os.chmod(dst, 0750)
			
		# ... and remove the temporary trac env
		shutil.rmtree(str(tmp_trac_dir))
		return

	def run(self):
		try:
			subcmd = getattr(self, 'subcmd_%s' % self.argv[0])
		except AttributeError:
			self.sa.execute(['help', 'trac'])	
			return

		subcmd(self.argv[1:])
