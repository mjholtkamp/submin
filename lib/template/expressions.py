# Based on calc.py, from http://www.dabeaz.com/ply/example.html

tokens = (
	'NAME','NUMBER',
	'PLUS','MINUS','TIMES','DIVIDE','EQUALS','ASSIGN',
	'LPAREN','RPAREN','QUOTE'
	)

# Tokens

t_PLUS	= r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_EQUALS  = r'=='
t_ASSIGN  = r'='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_QUOTE = r'\''
t_NAME	= r'[a-zA-Z_][a-zA-Z0-9_]*'

def t_NUMBER(t):
	r'\d+'
	try:
		t.value = int(t.value)
	except ValueError:
		raise "Integer value too large", t.value
		t.value = 0
	return t

# Ignored characters
t_ignore = " \t"

def t_newline(t):
	r'\n+'
	t.lexer.lineno += t.value.count("\n")

def t_error(t):
	raise "Illegal character '%s'" % t.value[0]
	t.lexer.skip(1)

# Build the lexer
import ply.lex as lex
lex.lex()

# Parsing rules

precedence = (
	('left','EQUALS'),
	('left','PLUS','MINUS'),
	('left','TIMES','DIVIDE'),
	('right','UMINUS'),
	)

# dictionary of names
names = {'pi' : 3.14 }

def p_statement_assign(t):
	'statement : NAME ASSIGN expression'
	names[t[1]] = t[3]

def p_statement_expr(t):
	'statement : expression'
	print t[1]

def p_statement_equals(t):
	'''expression : expression EQUALS expression
				  | NAME EQUALS NAME'''
	t[0] = t[1] == t[3]

def p_expression_binop(t):
	'''expression : expression PLUS expression
				  | expression MINUS expression
				  | expression TIMES expression
				  | expression DIVIDE expression'''
	if t[2] == '+'  : t[0] = t[1] + t[3]
	elif t[2] == '-': t[0] = t[1] - t[3]
	elif t[2] == '*': t[0] = t[1] * t[3]
	elif t[2] == '/': t[0] = t[1] / t[3]

def p_expression_uminus(t):
	'expression : MINUS expression %prec UMINUS'
	t[0] = -t[2]

def p_expression_group(t):
	'expression : LPAREN expression RPAREN'
	t[0] = t[2]

def p_expression_number(t):
	'expression : NUMBER'
	t[0] = t[1]

def p_expression_name(t):
	'expression : NAME'
	try:
		t[0] = names[t[1]]
	except LookupError:
		#print "Undefined name '%s'" % t[1]
		t[0] = 0

def p_error(t):
	raise "Syntax error at '%s'" % t.value

import ply.yacc as yacc
yacc.yacc()

def parse(s):
	yacc.parse(s)

if __name__ == "__main__":
	while 1:
		try:
			s = raw_input('calc > ')
		except EOFError:
			break
		except:
			pass
		try:
			yacc.parse(s)
		except:
			pass
