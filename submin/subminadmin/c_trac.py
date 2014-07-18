import os
import sys
import commands
import shutil
import re

SYSTEM_ENV_LINES = """
# Added by submin2-admin trac init
import os
os.environ['TRAC_ENV_PARENT_DIR'] = '%s'

"""

WSGI_ENV_LINES = """
	# Added by submin2-admin trac init
    environ.setdefault('trac.env_parent_dir', os.environ['TRAC_ENV_PARENT_DIR'])

"""

class c_trac():
	'''Trac support commands
Usage:
    trac init                      - (re)creates trac cgi/wsgi/fcgi scripts'''

	def __init__(self, sa, argv):
		self.sa = sa
		self.argv = argv

	def subcmd_init(self, argv):
		from submin.models import options
		from submin.subminadmin import trac
		"""Initialize trac
		Why not just distribute them with submin? Two reasons: one is because
		they might change with each version of trac, two is because those scripts
		have a different license and IANAL so this is easier (reason one should
		be enough anyway).
		"""
		tmp_trac_dir = options.env_path() + 'tmp-trac'
		tmp_deploy_dir = tmp_trac_dir + 'deploy'

		if not trac.exists():
			print "Could not find 'trac-admin' command. If you want to use Trac, please",
			print "install trac and run: `submin2-admin %s trac init`" % options.env_path()
			return

		# first, create a temp trac env, because 'deploy' needs a working trac
		# env (sigh)
		trac.initenv(str(tmp_trac_dir), 'dummy', 'svn', '/tmp/non-existing')

		# then generate the scripts
		trac.deploy(str(tmp_trac_dir), str(tmp_deploy_dir))

		# copy them to our cgi-bin
		cgi_bin_dir = options.env_path() + 'cgi-bin'
		for root, dirs, files in os.walk(str(tmp_deploy_dir + 'cgi-bin')):
			for filename in files:
				src = os.path.join(root, filename)
				dst = os.path.join(str(cgi_bin_dir), filename)
				self.generate_Xgi_script(src, dst)
		
		# ... and remove the temporary trac env
		shutil.rmtree(str(tmp_trac_dir))

		# finally, set all permissions and ownerships
		self.sa.execute(['unixperms', 'fix'])
		return

	def subcmd_hook(self, argv):
		"""This is hidden from help because it is not meant to be run, except
		from commit/receive hooks
		"""
		from submin.path.path import Path
		from submin.models import hookjobs
		from submin.models import options
		from submin.subminadmin import trac
		import urllib2

		if argv[0] != 'queue' or len(argv) != 4:
			print 'Unknown command'
			return

		vcs_type, repository, hooktype = argv[1:]
		content = ''.join(sys.stdin.readlines())
		print 'Notifying Trac of changes...'
		if hooktype == 'trac-sync' and 'refs/tags' in content:
			print('Skipping tag (no sync needed)')
			return

		hookjobs.queue(vcs_type, repository, hooktype, content)

		baseurl = Path(options.http_vhost()
					+ options.url_path('base_url_submin'))
		joburl = str(baseurl + 'hooks' + hooktype + vcs_type + repository)

		try:
			response = urllib2.urlopen(joburl)
		except urllib2.HTTPError as e:
			print('Job queued, but could not sync to "%s", HTTP error %u' %
				(joburl, e.code, ))
		except urllib2.URLError as e:
			print('Job queued, but URL invalid %s: %s' %
				(joburl, str(e)))
		else:
			xml = response.read()
			if 'success="True"' not in xml:
				print('Failed to sync:\n%s' % xml)
			# TODO: don't process XML with regexps...
			messages = re.sub('.*<errormsgs>(.*)</errormsgs>.*', '\\1', xml, flags=re.DOTALL)
			messages = re.sub('<msg>(.*)</msg>', '\\1\n', messages)
			if "" != messages:
				print('WARNING: Synced, but got some messages:\n%s' % messages)


	def generate_Xgi_script(self, src, dst):
		"""Copy CGI/FCGI/WSGI script with small adjustments
		Set environment to point to trac dir instead of generated temp-dir
		Because script are generated out of our control, try to keep adjustmenst
		as generic as possible."""
		from submin.models import options
		header = True
		with open(src, "r") as f_in:
			with open(dst, "w") as f_out:
				for line in f_in.readlines():
					# set env right after the first non-comment
					if header and '#' not in line:
						header = False
						trac_dir = str(options.env_path('trac_dir'))
						f_out.write(SYSTEM_ENV_LINES % trac_dir)

					f_out.write(line)

					# if wsgi application is detected, add environ to that
					# because it won't read from os.environ
					if 'def application(environ' in line:
						f_out.write(WSGI_ENV_LINES)
	
	def run(self):
		try:
			subcmd = getattr(self, 'subcmd_%s' % self.argv[0])
		except AttributeError:
			self.sa.execute(['help', 'trac'])	
			return

		subcmd(self.argv[1:])
