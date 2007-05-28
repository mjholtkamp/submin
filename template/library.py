class Library(object):
	commands = {}
	
	def has_command(self, command):
		if command in self.commands.keys():
			return True
		return False
		
	def execute(self, node, template):
		if node.command not in self.commands.keys():
			return None
		return self.commands[node.command](node, template)
	
	def register(self, name):
		def decorator(fn):
			self.commands[name] = fn
		return decorator