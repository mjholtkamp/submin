import os
from config.config import ConfigData
from path.path import Path
import shutil

class c_convert():
	'''Create a new configuration from an old-style config
Usage:
    convert <old-config-file>   - Interactively create new config from old'''

	def __init__(self, sa, argv):
		self.sa = sa
		self.argv = argv
		self.old_options = {}
		self.oldc = None
		self.import_svn = False
		self.import_trac = False

	def _get_options_from_config(self, section, option, store_as):
		self.old_options[store_as] = self.oldc.get(section, option)

	def _check_imports(self):
		"""Check if we should import svn and trac or just point to it. We
do this by checking if they reside in the same dirs as the auth files."""

		dirs = {}
		dirs['authz_file'] = self.old_options['authz_file']
		dirs['access_file'] = self.old_options['access_file']
		dirs['userprop_file'] = self.old_options['userprop_file']
		dirs['svn_dir'] = self.old_options['svn_dir']
		dirs['trac_dir'] = self.old_options['trac_dir']

		for d in dirs:
			dirs[d] = os.path.dirname(dirs[d])

		if dirs['authz_file'] == dirs['access_file'] and \
				dirs['authz_file'] == dirs['userprop_file']:
			if dirs['authz_file'] == dirs['svn_dir']:
				self.import_svn = True
			if dirs['authz_file'] == dirs['trac_dir']:
				self.import_trac = True

	def convert(self, oldconfig):
		# Because Config() is a singleton, we have to be careful with it.
		# We first want to use it for the old config, then initenv. In initenv
		# it will be used for the new config, so we have to read old config
		# before that. So, to make it easy on ourselves, we use ConfigData,
		# which is not a Singleton
		try:
			self.oldc = ConfigData(oldconfig)
		except IOError, e:
			print "Reading old config failed: %s" % str(e)
			return

		cmd_list = ['initenv', 'create_user=no']

		# get options that we need to pass to initenv
		self._get_options_from_config('svn', 'repositories', 'svn_dir')
		self._get_options_from_config('www', 'base_url', 'submin_url')
		self._get_options_from_config('www', 'trac_base_url', 'trac_url')
		self._get_options_from_config('www', 'svn_base_url', 'svn_url')
		self._get_options_from_config('trac', 'basedir', 'trac_dir')

		# copy this list, because we don't want the other options
		initenv_options = self.old_options.copy()

		# get some more options, we need later on
		self._get_options_from_config('svn', 'authz_file', 'authz_file')
		self._get_options_from_config('svn', 'access_file', 'access_file')
		self._get_options_from_config('svn', 'userprop_file', 'userprop_file')
		self._get_options_from_config('svn', 'repositories', 'svn_dir')
		self._get_options_from_config('trac', 'basedir', 'trac_dir')

		# now see if we need to change options
		self._check_imports()
		if (self.import_svn):
			initenv_options['svn_dir'] = 'svn'
		if (self.import_trac):
			initenv_options['trac_dir'] = 'trac'
		
		# now finally build the options list
		for (key, value) in initenv_options.iteritems():
			cmd_list.append('%s=%s' % (key, value))

		# call initenv
		if not self.sa.execute(cmd_list):
			return

		# we now have our environment, so we can create a config object
		os.environ['SUBMIN_ENV'] = self.sa.env
		newc = ConfigData()

		# copy svn/trac data, if necessary
		new_svn_dir = str(newc.getpath('svn', 'repositories'))
		new_trac_dir = str(newc.getpath('trac', 'basedir'))
		if self.import_svn:
			self._copy_dir(self.old_options['svn_dir'], new_svn_dir)
		if self.import_trac:
			self._copy_dir(self.old_options['trac_dir'], new_trac_dir)

		# copy users/groups/permissions

	def _copy_dir(self, old_dir, new_dir):
		os.rmdir(new_dir) # copytree will fail otherwise
		shutil.copytree(old_dir, new_dir)

	def run(self):
		if len(self.argv) != 1:
			self.sa.execute(['help', 'convert'])
			return

		self.convert(self.argv[0])
