import re
import os
import sys
import string
from pprint import pprint

from library import Library

class UnknownCommandError(Exception):
	pass

class Node(object):
	"""Represents a piece of template-text.
	This is the most basic node and basically does not convey meaning."""
	
	def __init__(self, type, previous_node, line):
		self.type = type
		self.previous_node = previous_node
		self.line = line
		
		self.nodes = []
	
	def evaluate(self, template=None):
		"""Even the most basic node has a evaluate function, although it 
		returns an empty string.
		Subclasses of Node must implement their own evaluate function, to 
		ensure a template is evaluated completely"""
		return ''
		
	def __str__(self):
		return '<%s :- %s>' % (self.type, ''.join([str(x) for x in self.nodes]))
	
	def __repr__(self):
		return str(self)

class TextNode(Node):
	"""Represents only text, usually HTML."""
	def __init__(self, content, previous_node, line):
		super(TextNode, self).__init__('text', previous_node, line)
		self.content = content
	
	def evaluate(self, template=None):
		return self.content
	
	def __str__(self):
		return '<text %r>' % self.content

class CommandNode(Node):
	"""Represents a command.
	A command can have arguments and/or input-text (both optional). 
	The syntax is: [command:arguments input-text].
	The input-text can also contain commands, which are not evaluated unless
	the corresponding command does so.
	"""
	def __init__(self, command, previous_node, line):
		super(CommandNode, self).__init__('command', previous_node, line)
		self.command = command
		self.arguments = ''
	
	def evaluate(self, template):
		library = Library()
		if library.has_command(self.command):
			return library.execute(self, template)
		raise UnknownCommandError, self.command
	
	def __str__(self):
		if self.arguments:
			return '<cmd %s(%s) :- %s>' % (self.command, self.arguments, 
				'\n\t'.join([str(x) for x in self.nodes]))
		return '<cmd %s :- %s>' % (self.command, '\n\t'.join([str(x) for x in self.nodes]))

ESCAPE, COMMAND, ARGUMENTS = range(3)
class Parser(object):
	"""A Parser takes a template-string and creates a tree of nodes.
	"""
	def __init__(self, template):
		self.template = template
		self.stack = []
		self.open_cmds = 0
		self.state = None
		self.data = ''
		self.lines = 1
	
	def parse(self):
		for ch in self.template:
			previous_node = None
			if len(self.stack):
				previous_node = self.stack[-1]


			# FIXME: Escaping gaat nog niet goed als er geen \, [ of ] erna 
			# komt: dan blijft het geheel in state ESCAPE.
			
			if ch == '\\' and self.state != ESCAPE:
				prev_state = self.state
				self.state = ESCAPE
			elif ch in ('\\', '[', ']') and self.state == ESCAPE:
				# Escape characters
				# self.state = None
				self.data += ch
				self.state = prev_state
			elif ch == '[':
				# Add new CommandNode to the stack
				
				if not self.state and self.data:
					# But first, do some text cleaning-up!
					text = TextNode(self.data, previous_node, self.lines)
					previous_node = text
					self.data = ''
					if self.open_cmds:
						self.stack[-1].nodes.append(text)
					else:
						self.stack.append(text)
				
				self.state = COMMAND
				self.stack.append(CommandNode('', previous_node, self.lines))
				self.open_cmds += 1
			elif (ch.isspace() or ch in (':', '.')) and self.state == COMMAND:
				# Represents the end of the command-section. Set the node's
				# command-name.
				# The : and . characters also represent the beginning of the
				# argument-section of the command.
				self.stack[-1].command = self.data
				self.data = ''
				if ch == '\n':
					# A newline is usually explicitly there to keep your html tidy
					self.data = '\n'
				if ch in (':', '.'):
					self.state = ARGUMENTS
				else:
					self.state = None
			elif ch == '.' and self.state == ARGUMENTS:
				# Ignore subsequent dots, add them to the arguments
				self.data += ch
			elif ch.isspace() and self.state == ARGUMENTS:
				# End of the arguments section, fill in the arguments of the
				# node
				self.stack[-1].arguments = self.data
				self.data = ''
				if ch == '\n':
					# A newline is usually explicitly there to keep your html tidy
					self.data = '\n'
				self.state = None
			elif ch == ']':
				# The end of a command. Now there is some heavy stuff that 
				# needs to be done:
				if self.data and not self.state == COMMAND \
						and not self.state == ARGUMENTS:
					# Add a TextNode to the CommandNode with the remaining
					# character-data
					text = TextNode(self.data, previous_node, self.lines)
					previous_node = text
					self.data = ''
					self.stack[-1].nodes.append(text)
					
				if self.state == COMMAND:
					# The command has no character-data, but we need to
					# finish the command-section
					self.stack[-1].command = self.data
					self.data = ''
				elif self.state == ARGUMENTS:
					# The command has no character data, but we need to
					# finish the arguments-section
					self.stack[-1].arguments = self.data
					self.data = ''
					
				self.open_cmds -= 1

				if self.open_cmds:
					# The current CommandNode is embedded in another command.
					# We need to add this node to the other Node.
					node = self.stack.pop()
					# Add the node to the other's node-stack
					self.stack[-1].nodes.append(node)
				
				self.state = None
			else:
				# Just character data!
				self.data += ch

			if ch == '\n':
				# Keep track of where we are in the file!
				self.lines += 1
	
		if self.data:
			# If we have some data left at the end of the template, create
			# a TextNode for it.
			self.stack.append(TextNode(self.data, previous_node, self.lines))
		return self.stack

class Template(object):
	def __init__(self, template, variables={}):
		if hasattr(template, 'readlines'):
			self.template_string = ''.join(template.readlines())
			self.filename = os.path.join(os.getcwd(), template.name)
		else:
			self.template_string = template
			self.filename = 'string'
		self.variables = variables.copy()
		self.node_variables = {}
		
		parser = Parser(self.template_string)
		self.nodes = parser.parse()
	
	def __del__(self):
		self.template_string = None
		self.variables = None
		self.node_variables = None
		self.nodes = None
	
	def parse_tree(self):
		"""Returns the parse tree as a string"""
		return '\n'.join([str(x) for x in self.nodes])
		
	def evaluate(self):
		"""Returns the evaluated template as a string"""
		evaluated_string = ''
		for node in self.nodes:
			evaluated_string += node.evaluate(self)
		return evaluated_string
		
	def variable_value(self, key='', attr=None, variable=None, recursing=False):
		"""Looks up a key in a variable.
		If the variable is not provided, it is found in self.variables
		if key is in the form of key.attribute, the attribute value of key is 
		returned. 
		
		It first tries if attribute is a function and returns the return value
		of that function. Secondly it tries if attribute is a dictionary key
		and returns it's value. Thirdly it tries if attribute is a data-member
		and returns it. Next it checks if attribute is a digit, for a 
		list-lookup.
		If that that all fails, it returns None.
		"""
		if '.' in key:
			key, attr = key.split('.', 1)
		if variable is None or recursing:
			if variable is None:
				variable = self.variables
			if not variable.has_key(key) and key not in self.node_variables:
				return None
			if key in self.node_variables:
				variable = self.node_variables[key][-1]
			else:
				variable = variable.get(key, None)
		
		# No attribute, just return the variable
		if not attr:
			return variable
		
		if '.' in attr:
			# recurse until we have it all broken down!
			return self.variable_value(key=attr, variable=variable, recursing=True)
		
		# Do all the checks
		if hasattr(variable, attr):
			attr = getattr(variable, attr)
			if hasattr(attr, '__call__'):
				return attr()
			return attr
		if hasattr(variable, 'has_key') and variable.has_key(attr):
			return variable[attr]
		if attr.isdigit():
			if len(variable) <= int(attr):
				return None
			return variable[int(attr)]
		
		return None
