from config.config import Config
from path.path import Path

class UIScenarios(object):
	def __init__(self, filename=None):
		if filename is None:
			filename = Config().get("tests", "scenarios_file")
		self.filename = filename
		self.sections = []

		self.browsers = ["Safari 3", "Firefox 2", "Firefox 3", "IE 7"]

		self._parse()

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
				self.sections[-1]["options"].append(line.strip().split("\t"))
