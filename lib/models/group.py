class Group:
	def __init__(self, name, users = []):
		self.name = name
		self.users = '[ '
		for user in users:
			self.users += "'" + user + "', "
		self.users = self.users[:-2] + ' ]'

	def __str__(self):
		return self.name
