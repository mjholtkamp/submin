from template.shortcuts import evaluate_main
from dispatch.response import Response, XMLStatusResponse
from dispatch.view import View
from auth.decorators import *

class Intro(View):
	@login_required
	def handler(self, req, path):
		if req.is_ajax():
			return self.ajaxhandler(req, path)

		localvars = {}

		formatted = evaluate_main('intro', localvars)
		return Response(formatted)

	def ajaxhandler(self, req, path):
		return XMLStatusResponse(False, 'operations for intro are not implemented')

