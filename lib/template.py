#!/usr/bin/python

import re
import sys
import string

html_quote_sequence = [
	(u'&', u'&amp;')
]

this_module = sys.modules[__name__]

def quote_html(text, markup_newlines=False):
	""" Convert special HTML characters to &xyz; form.
		If <markup_newlines>, convert newlines into <p> tags, etc. """

	for a, b in html_quote_sequence:
		text = text.replace(a, b)

	return text

def _split_command(thing):
	""" (markup helper function) """
	# ugliness because everything in html

	match = re.search('(\s|\<p\>)', thing)
	if match == None:
		command = thing
		text = u''
	else:
		command = thing[:match.start()]
		text = thing[match.end():]

	command = command.replace('-','_').lower()

	return command, text


def markup(text, meta=None, localvars={}, outermost=True):
	""" Markup language translator.
		Markup language is less ugly than html, a la wiki.
		Returns html text, modifies meta if given.
		localvars is a dictionary containing localvars

		If the result will be used by another call to markup with
		the same meta, set outermost to False.
		(necessary to get postprocessing step right)

		Special characters: [ ] \
		Escaping: \[ \] \\

		[blah some text]  results in a call to a function called markup_blah
	"""

	if meta is None: meta = { }

	chunks = re.split(ur'(\[|\]|\\\[|\\\]|\\\\)', text)

	stack = [ u'' ]
	context_stack = [ { } ]

	for chunk in chunks:
		if chunk == '[':
			stack.append(u'')
			context_stack.append({ })
		elif chunk == ']' and len(stack) >= 2:
			thing = stack.pop(-1)
			thing_context = context_stack.pop(-1)

			command, text = _split_command(thing)

			if len(stack) >= 2:
			    context = u'context_' + _split_command(stack[-1])[0]
			    context = getattr(this_module,context,[ ])
			else:
			    context = [ ]

			if command in context:
			    context_stack[-1][str(command)] = text
			    text = u''
			elif command + u'*' in context:
			    context_stack[-1][str(command)] = \
					context_stack[-1].get(str(command),[ ]) + [ text ]
			    text = u''
			else:
			    try:
					cmdargs = re.split('[:.]', command)
					text = getattr(this_module, 'markup_'+cmdargs[0])(cmdargs[1:], text, meta, localvars, **thing_context)
			    except AttributeError:
					import StringIO, traceback
					string_file = StringIO.StringIO()
					traceback.print_exc(file=string_file)
					text = u'<b><pre>'+quote_html(string_file.getvalue())+u'</pre></b>'
			stack[-1] = stack[-1] + text
		else:
			if chunk in (u'\\]',u'\\[',u'\\\\'):
			    chunk = chunk[1]

			stack[-1] = stack[-1] + quote_html(chunk, True)

	# should only be one item on stack, but don't freak if there's more
	result = string.join(stack,u'')

	if outermost:
		for mark, callback in meta.get('_callbacks',[]):
			value = callback()
			result = result.replace(mark, value)

	return result

_callback_counter = 0xe000 # Unicode private use area
def make_callback_mark(meta, callback):
	""" Utility for markup_ functions:
		Return a special unicode character indicating that
		the result of callback() should be inserted here.

		The callback will be called *after* all markup has occured.
		This allows inserting variables that have not been set yet,
		and such. """

	global _callback_counter
	mark = unichr(_callback_counter)
	_callback_counter += 1

	meta['_callbacks'] = meta.get('_callbacks',[]) + [(mark, callback)]
	return mark

def markup_ival(args, text, meta=None, localvars={}, **varargs):
	if not args:
		return '[ival]'

	return '[ival.' + ' '.join(args) + ']'

def markup_iter(args, text, meta=None, localvars={}, **varargs):
	if not localvars.has_key(args[0]):
		return ''

	iterarray = ''
	for var in localvars[args[0]]:
		newtext = text
		if type(var) is str or hasattr(var, '__str__'):
			newtext = newtext.replace('[ival]', str(var))

		matches = re.findall('(\[ival\.([^\]]+)\])', newtext)
		for match in matches:
			newtext = re.sub(re.escape(match[0]),
					getattr(var, match[1], ''), newtext)

		iterarray += newtext

	return iterarray

def markup_set(args, text, meta=None, localvars={}, **varargs):
	if text == 'true' or text == 'True':
		localvars[args[0]] = True
	else:
		localvars[args[0]] = text
	return ''

def markup_val(args, text, meta=None, localvars={}, **varargs):
	if localvars.has_key(text):
		if localvars[text] is True:
			return 'true'
		else:
			if localvars[text] is False:
				return 'false'
		return localvars[text]
	return ''

def markup_test(args, text, meta=None, localvars={}, **varargs):
	if localvars.has_key(args[0]) and localvars[args[0]] is True:
		return text
	return ''

def markup_include(args, text, meta=None, localvars={}, **varargs):
	import os
	from os import path

	if not os.path.exists(text):
		return 'Couldn\'t include %s' % text

	dirname = path.dirname(text)
	if dirname:
		oldcwd = os.getcwd()
		os.chdir(path.dirname(text))

	fd = open(path.basename(text), 'r')
	lines = ''
	if fd != None:
		lines = ''.join(fd.readlines())
		if len(lines) > 0:
			lines = markup(lines[:-1], localvars=localvars)

		fd.close()

	if dirname:
		os.chdir(oldcwd)

	return lines

def test():
	template="""[set:test2 5][include ../templates/test][set:test 3]here be dragons
[val test][set:bla true][set:waarheid true]
[val test2][set:bla test][set:test 42]
This will give no error or warning: [val test3]
[iter:users some html [ival] code here<br />] 
[test:waarheid The variable bla is set to '[val bla]'<br />]
{else xhtml code here<br />}"""

	localvars = {}
	users = ['sabre2th', 'avaeq', 'will', 'tux']
	localvars['users'] = users
	print markup(template, None, localvars)

if __name__ == "__main__":
	test()
