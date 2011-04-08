from submin.template.shortcuts import evaluate
from submin.dispatch.response import Response
from submin.dispatch.view import View
from submin.auth.decorators import *
from submin.models.uiscenarios import UIScenarios as UIScenariosModel

class UIScenarios(View):
	@admin_required
	def handler(self, req, path):
		uiscenarios = UIScenariosModel()
		if req.post:
			uiscenarios.clean_state()
			for key in req.post:
				uiscenarios.set_state(key, req.post[key])
			uiscenarios.save_state()
		localvars = {}
		localvars["sections"] = uiscenarios.sections
		localvars["browsers"] = uiscenarios.browsers

		# Don't need sidebar
		formatted = evaluate('tests/uiscenarios.html', localvars)
		return Response(formatted)
