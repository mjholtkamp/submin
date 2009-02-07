class c_quit():
	'''Quits the program
Well, what more do you want to know about quit?'''

	def __init__(self, sa, argv):
		self.sa = sa

	def run(self):
		self.sa.quit = True
