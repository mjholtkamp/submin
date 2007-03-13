from cStringIO import StringIO

def mimport(moduleName):
	module = None
	try:
		from mod_python import apache
		module = apache.import_module(moduleName, autoreload=True)
# TODO: remove
		module = reload(module)
	except ImportError:
		module = __import__(moduleName, globals(), locals(), \
				moduleName.split('.')[:-1])

	return module

def iif(condition, ifTrue, ifFalse):
	if condition: return ifTrue
	return ifFalse

class Buffer:
	def __init__(self):
		self.data = StringIO()

	def write(self, *args):
		self.data.write(''.join(args))
		#for arg in args:
			#print >>self.data, str(arg),
		#print >>self.data

	def __str__(self):
		return self.data.getvalue()

	def getvalue(self):
		return str(self)
