import cPickle
from distutils.dep_util import newer

from config.config import Config
from path.path import Path

class UIScenarios(object):
	"""Create a list of sections with lists of options.
	Needs a file with sections / options in this format:
		A section is a tab-separated line, starting with "="
		An option is a tab-separated line (the tab separatas table-cells)

	Saves this list of sections to a pickled file, which is reset when the
	file with option-texts is newer than the pickled file.
	"""
	def __init__(self, filename=None):
		if filename is None:
			filename = Config().get("tests", "scenarios_file")
		self.filename = filename

		# Don't randomly change this order! Code below uses indexes to refer
		# to these browsers and does not rebuild those indexes when getting
		# data from pickled-file.
		self.browsers = ["Safari 3", "Firefox 2", "Firefox 3", "IE 7", "Opera 9"]

		self.sections = []
		# Should we get the sections from .txt file or pickled (".saved") file?
		if newer(self.filename, self.filename + ".saved"):
			self._parse()
		else:
			self.sections = self.load_state()

	def _parse(self):
		fp = open(self.filename)
		for line in fp:
			if not line.strip():
				continue

			if line.startswith("="):
				self.sections.append(
						{"heading": line.lstrip("=").strip().split("\t"),
							"options": []})
			else:
				optiondict = {}
				optiondict["texts"] = line.strip().split("\t")
				# Flags default to False
				optiondict["flags"] = [False for i in self.browsers]
				optiondict["hash"] = hash(line)
				self.sections[-1]["options"].append(optiondict)

	def clean_state(self):
		"""Sets all flags to False for every option."""
		for section in self.sections:
			for option in section["options"]:
				option["flags"] = [False for i in self.browsers]

	def set_state(self, hash_value, flags):
		# Currently only tested for CGI!
		for section in self.sections:
			for option in section["options"]:
				if str(option["hash"]) != str(hash_value):
					continue
				try:
					for flag in flags:
						option["flags"][int(flag.value)] = True
				except TypeError:
					option["flags"][int(flags.value)] = True

	def save_state(self, write=True):
		fp = open(self.filename + ".saved", "wb")
		cPickle.dump(self.sections, fp)
		fp.close()

	def load_state(self):
		sections = []
		try:
			fp = open(self.filename + ".saved", "rb")
			sections = cPickle.load(fp)
			fp.close()
		except:
			pass
		return sections
