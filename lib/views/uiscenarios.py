from template import evaluate
from dispatch.response import Response
from dispatch.view import View
from auth.decorators import *
from models.uiscenarios import UIScenarios as UIScenariosModel

class UIScenarios(View):
	@admin_required
	def handler(self, req, path):
		uiscenarios = UIScenariosModel()
		localvars = {}
		localvars["sections"] = uiscenarios.sections
		localvars["browsers"] = uiscenarios.browsers

		formatted = evaluate('tests/uiscenarios.html', localvars)
		return Response(formatted)
