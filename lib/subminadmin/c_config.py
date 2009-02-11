from path.path import Path
from config.config import ConfigData

class c_config():
	'''Commands to change config
Usage:
	config defaults                           - create config with defaults
	config get                                - list everything
	config get <section>                      - list options in section
	config get <section> <option>             - get config value in section
	config set <section> <option> <value>     - set config value in section'''

	def __init__(self, sa, argv):
		self.sa = sa
		self.argv = argv

	def subcmd_defaults(self, argv):
		conf_path = str(Path(self.sa.env) + 'conf' + 'submin.ini')
		# set defaults

	def subcmd_get(self, argv):
		print argv

	def subcmd_set(self, argv):
		print argv

	def run(self):
		if len(self.argv) < 1:
			self.sa.execute(['help', 'config'])
			return

		try:
			subcmd = getattr(self, 'subcmd_%s' % self.argv[0])
		except AttributeError:
			self.sa.execute(['help', 'config'])
			return

		subcmd(self.argv[1:])
