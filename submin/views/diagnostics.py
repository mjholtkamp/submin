from submin.template.shortcuts import evaluate_main
from submin.dispatch.response import Response
from submin.dispatch.view import View
from submin.auth.decorators import admin_required
from submin.models import options
from submin.diagnostics import trac, git, svn

class Diagnostics(View):
	@admin_required
	def handler(self, req, path):
		localvars = {}

		diagnostics = {}
		diagnostics.update(trac.diagnostics())
		diagnostics.update(svn.diagnostics())
		diagnostics.update(git.diagnostics())
		localvars['diag'] = diagnostics
		localvars['subminenv'] = options.env_path()

		formatted = evaluate_main('diagnostics.html', localvars, request=req)
		return Response(formatted)
