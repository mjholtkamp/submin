class Group:
	def __init__(self, name, users = []):
		self.name = name
		self.users = users

	def __str__(self):
		return self.name
