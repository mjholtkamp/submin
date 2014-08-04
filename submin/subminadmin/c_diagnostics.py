class c_diagnostics():
	'''Run diagnostics on submin
Usage:
    diagnostics [<type>]  - run diagnostics of type <type>

    Where <type> is one of: 'all', 'email', 'git', 'svn', 'trac' or nothing.
    When the <type> is 'all' or nothing, all diagnostics are run, otherwise
    only the selected category is run (e.g. 'diagnostics email' to only run
    email diagnostics. When all diagnostics are run, a summary is given at
    the end.'''
	needs_env = True

	def __init__(self, sa, argv):
		self.sa = sa
		self.argv = argv

	def run(self):
		from submin.models import options
		from submin.template.shortcuts import evaluate
		from submin.diagnostics import trac, git, svn, email

		localvars = {}

		diagnostics = {}
		if len(self.argv) > 0:
			which = self.argv[0]
		else:
			which = 'all'

		if which in ('all', 'email'):
			diagnostics.update(email.diagnostics())
		if which in ('all', 'git'):
			diagnostics.update(git.diagnostics())
		if which in ('all', 'svn'):
			diagnostics.update(svn.diagnostics())
		if which in ('all', 'trac'):
			diagnostics.update(trac.diagnostics())
		localvars['diag'] = diagnostics
		localvars['subminenv'] = options.env_path()

		formatted = evaluate('diagnostics.%s.print' % (which,), localvars)
		print(formatted)
