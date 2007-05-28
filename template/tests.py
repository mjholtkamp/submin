import unittest

from template import Template
# import template
import template_commands
template_commands.DEBUG = False

def evaluate(tpl_string, variables={}):
	tpl = Template(tpl_string, variables)
	return (tpl, tpl.evaluate())


class SetTagTest(unittest.TestCase):
	def testEvaluatesEmpty(self):
		tpl, ev = evaluate('[set:foo bar]')
		self.assertEquals(ev, '')
	
	def testVariablesSetCorrect(self):
		tpl, ev = evaluate('[set:foo bar]')
		self.assertEquals(tpl.variables, {'foo': 'bar'})
	
	def testMissingArgument(self):
		tpl = Template('[set bar]')
		self.assertRaises(template_commands.MissingRequiredArguments, tpl.evaluate)

class ValTagTest(unittest.TestCase):
	def testNonEmpty(self):
		tpl, ev = evaluate('[val foo]', {'foo': 'bar'})
		self.assertNotEqual(ev, '')
	
	def testCorrectValue(self):
		tpl, ev = evaluate('[val foo]', {'foo': 'bar'})
		self.assertEquals(ev, 'bar')
	
	def testEmptyValue(self):
		tpl, ev = evaluate('[val foo]', {'baz': 'bar'})
		self.assertEquals(ev, '')
	
	def testMissingArgument(self):
		tpl = Template('[val]')
		self.assertRaises(template_commands.MissingRequiredArguments, tpl.evaluate)

class IterTagTest(unittest.TestCase):
	def testCorrectValue(self):
		tpl, ev = evaluate('[iter:range bar]', {'range': range(10)})
		correctValue = ''.join(['bar' for x in range(10)])
		self.assertEquals(ev, correctValue)
	
	def testMissingArgument(self):
		tpl = Template('[iter bar]')
		self.assertRaises(template_commands.MissingRequiredArguments, tpl.evaluate)
	
	def testEmptyForUnknown(self):
		tpl, ev = evaluate('[iter:range bar]')
		self.assertEquals(ev, '')
	
	def testEmptyValue(self):
		tpl, ev = evaluate('[iter:range bar]', {'range': []})
		self.assertEquals(ev, '')

class IvalTagTest(unittest.TestCase):
	def testCorrectValue(self):
		tpl, ev = evaluate('[iter:range [ival]]', {'range': range(10)})
		correctValue = ''.join([str(x) for x in range(10)])
		self.assertEquals(ev, correctValue)
	
	def testCorrectValueObject(self):
		class objectTest:
			def __init__(self, attr): self.attr = attr
		l = []
		for attr in range(10):
			l.append(objectTest(attr))
		tpl, ev = evaluate('[iter:list [ival.attr]]', {'list': l})
		correctValue = ''
		for i in l:
			correctValue += str(i.attr)
		self.assertEquals(ev, correctValue)

class TestTest(unittest.TestCase):
	def testCorrectValue(self):
		tpl, ev = evaluate('[test:foo bar]', {'foo': 'bar'})
		self.assertEquals(ev, 'bar')
	
	def testEmptyValue(self):
		tpl, ev = evaluate('[test:foo bar]')
		self.assertEquals(ev, '')
	
	def testMissingArgument(self):
		tpl = Template('[test foo]')
		self.assertRaises(template_commands.MissingRequiredArguments, tpl.evaluate)
	
	def testEmptyText(self):
		tpl, ev = evaluate('[test:foo]', {'foo': 'bar'})
		self.assertEquals(ev, '')
	
	def testCorrectValueObject(self):
		class Foo: bar = 'baz'
		
		tpl, ev = evaluate('[test:foo.bar baz]', {'foo': Foo()})
		self.assertEquals(ev, 'baz')
	
class ElseTest(unittest.TestCase):
	def testCorrectValue(self):
		tpl, ev = evaluate('[test:foo bar][else baz]')
		self.assertEquals(ev, 'baz')
	
	def testWhiteSpaceBeforeElse(self):
		tpl, ev = evaluate('[test:foo bar] [else baz]')
		self.assertEquals(ev, ' baz')

	def testTestSucceeds(self):
		tpl, ev = evaluate('[test:foo bar][else baz]', {'foo': 'quux'})
		self.assertEquals(ev, 'bar')
	
	def testRaiseElseError(self):
		tpl = Template('[val bar][else baz]')
		self.assertRaises(template_commands.ElseError, tpl.evaluate)

# TODO: write tests for include!

if __name__ == "__main__":
	unittest.main()