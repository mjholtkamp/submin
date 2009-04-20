import unittest
from tempfile import mkstemp
import os

from template import Template
# import template
import template_commands
template_commands.DEBUG = False

def evaluate(tpl_string, variables={}):
	'Helper function for the tests.'
	tpl = Template(tpl_string, variables)
	return (tpl, tpl.evaluate())


class SetTagTest(unittest.TestCase):
	'Testcase for the set-tag which can set a template variable'

	def testEvaluatesEmpty(self):
		tpl, ev = evaluate('[set:foo bar]')
		self.assertEquals(ev, '')

	def testVariablesSetCorrect(self):
		tpl, ev = evaluate('[set:foo bar]')
		self.assertEquals(tpl.variables, {'foo': 'bar'})

	def testMissingArgument(self):
		tpl = Template('[set bar]')
		self.assertRaises(template_commands.MissingRequiredArguments, tpl.evaluate)

	def testDotInArgument(self):
		tpl = Template('[set:foo.bar true]')
		self.assertRaises(template_commands.DotInLocalVariable, tpl.evaluate)

class ValTagTest(unittest.TestCase):
	'Testcase for the val-tag which inserts the value for a variable'

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
	'Testcase for the iter-tag, which iterates over a sequence'
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
	'Tests the ival-tag, which returns the current iteration-value'

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
	'Testcase for the test-tag.'

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

	def testNegationOfValueObject(self):
		class Foo: bar = False

		tpl, ev = evaluate('[test:!foo.bar baz]', {'foo': Foo()})
		self.assertEquals(ev, 'baz')

	def testNegationOfTrue(self):
		tpl, ev = evaluate('[test:!foo baz]', {'foo': True})
		self.assertEquals(ev, '')

	def testNegationOfFalse(self):
		tpl, ev = evaluate('[test:!foo baz]', {'foo': False})
		self.assertEquals(ev, 'baz')

	def testNegationOfNone(self):
		tpl, ev = evaluate('[test:!foo baz]', {'foo': None})
		self.assertEquals(ev, 'baz')

	def testNegationOfNoVariable(self):
		tpl, ev = evaluate('[test:!foo baz]', {})
		self.assertEquals(ev, 'baz')

class TestIterTest(unittest.TestCase):
	'Testcase for special iter-variables like ilast'

	def testTestIlast(self):
		tpl, ev = evaluate('[iter:range [ival][test:ilast last!]]', {'range': range(10)})
		self.assertEquals(ev, '0123456789last!')

	def testTestNotIlast(self):
		tpl, ev = evaluate('[iter:range [test:!ilast [ival]]]', {'range': range(10)})
		self.assertEquals(ev, '012345678')

class ElseTest(unittest.TestCase):
	'Testcase for the else-tag.'

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

	def testNegationElse(self):
		tpl, ev = evaluate('[test:!foo bar][else baz]', {'foo': True})
		self.assertEquals(ev, 'baz')

	def testElseInIter(self):
		tpl, ev = evaluate('[iter:range [test:foo evals true][else evals false]', {'range': range(10)})
		self.assertEquals(ev, 'evals false'*10)

	def testElseInSet(self):
		tpl, ev = evaluate('[set:range [test:foo evals true][else evals false]]')
		self.assertEquals(ev, '')

	def testEqualsBeforeElseFalse(self):
		tpl, ev = evaluate('[set:empty ][equals:errormsg:empty][else evals false]')
		self.assertEquals(ev, 'evals false')

	def testEqualsBeforeElseTrue(self):
		tpl, ev = evaluate('[set:one 1][set:een 1][equals:een:one evals true][else evals false]')
		self.assertEquals(ev, 'evals true')

class VariableValueTests(unittest.TestCase):
	'''Testcase for the variable_value function of a template-object

	variable_value can parse the variable name in various ways, see it's
	documentation in template.py'''

	def testVariables(self):
		tpl = Template('', {'foo': 'bar'})
		self.assertEquals(tpl.variable_value('foo'), 'bar')

	def testObjectVariables(self):
		class Foo:
			bar = 'baz'
		tpl = Template('', {'foo': Foo()})
		self.assertEquals(tpl.variable_value('foo.bar'), 'baz')

	def testDictVariables(self):
		tpl = Template('', {'foo': {'bar': 'baz'}})
		self.assertEquals(tpl.variable_value('foo.bar'), 'baz')

	def testNodeVariables(self):
		tpl = Template('')
		tpl.node_variables['ival'] = ['foo']
		self.assertEquals(tpl.variable_value('ival'), 'foo')

class IncludeTests(unittest.TestCase):
	'Testcase for the include-tag'

	def setUp(self):
		"""Creates a temporary file for inclusion"""
		# mkstemp returns a filedescriptor, which is an int. Open the file
		# with os.fdopen.
		fd, self.filename = mkstemp()
		self.text = 'SILENCE! I keel joe!\n'
		filehandle = os.fdopen(fd, 'w+')
		filehandle.write(self.text)
		filehandle.close()

	def tearDown(self):
		"""Removes the temporary file"""
		os.unlink(self.filename)

	def testInclude(self):
		tpl, ev = evaluate('[include %s]' % self.filename)
		self.assertEquals(ev, self.text)

	def testDoesNotIncludeInTest(self):
		tpl, ev = evaluate('[test:do_include [include %s]]' % self.filename,
				{'do_include': False})
		self.assertEquals(ev, '')

	def testDoesIncludeInTest(self):
		tpl, ev = evaluate('[test:do_include [include %s]]' % self.filename,
				{'do_include': True})
		self.assertEquals(ev, self.text)

def runtests():
	unittest.main()

if __name__ == "__main__":
	runtests()
