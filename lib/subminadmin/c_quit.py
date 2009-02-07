class c_quit():
	"""Quits the program"""
	def __init__(self, sa, argv):
		self.sa = sa

	def run(self):
		self.sa.quit = True
