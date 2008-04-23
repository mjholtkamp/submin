from template import evaluate
from dispatch.response import Response
from dispatch.view import View
from auth.decorators import *
from models.uiscenarios import UIScenarios as UIScenariosModel

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
