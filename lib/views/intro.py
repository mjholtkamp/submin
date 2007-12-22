from template.shortcuts import evaluate_main
from dispatch.response import Response, XMLStatusResponse
from dispatch.view import View
from config.config import Config

class Intro(View):
	def handler(self, req, path):
		if req.is_ajax():
			return self.ajaxhandler(req, path)

		config = Config()

		localvars = {}

		formatted = evaluate_main('intro', localvars)
		return Response(formatted)

	def ajaxhandler(self, req, path):
		config = Config()

		return XMLStatusResponse(False, 'operations for intro are not implemented')

