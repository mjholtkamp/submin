import os
from config.config import ConfigData
from path.path import Path

class c_convert():
	'''Create a new configuration from an old-style config
Usage:
    convert <old-config-file>   - Interactively create new config from old'''

	def __init__(self, sa, argv):
		self.sa = sa
		self.argv = argv
		self.old_options = {}
		self.oldc = None

	def _get_options_from_config(self, section, option, store_as):
		self.old_options[store_as] = self.oldc.get(section, option)

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
		
		self._get_options_from_config('svn', 'repositories', 'svn_dir')
		self._get_options_from_config('www', 'base_url', 'submin_url')
		self._get_options_from_config('www', 'trac_base_url', 'trac_url')
		self._get_options_from_config('www', 'svn_base_url', 'svn_url')
		self._get_options_from_config('trac', 'basedir', 'trac_dir')
		for (key, value) in self.old_options.iteritems():
			cmd_list.append('%s=%s' % (key, value))

		self.sa.execute(cmd_list)

	def run(self):
		if len(self.argv) != 1:
			self.sa.execute(['help', 'convert'])
			return

		self.convert(self.argv[0])
