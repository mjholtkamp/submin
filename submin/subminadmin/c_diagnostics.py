class c_diagnostics():
	'''Run diagnostics on submin'''
	needs_env = True

	def __init__(self, sa, argv):
		self.sa = sa

	def run(self):
		from submin.models import options
		from submin.template.shortcuts import evaluate
		from submin.diagnostics import trac, git, svn, email

		localvars = {}

		diagnostics = {}
		diagnostics.update(trac.diagnostics())
		diagnostics.update(svn.diagnostics())
		diagnostics.update(git.diagnostics())
		diagnostics.update(email.diagnostics())
		localvars['diag'] = diagnostics
		localvars['subminenv'] = options.env_path()

		formatted = evaluate('diagnostics.print', localvars)
		print(formatted)
