from template.shortcuts import evaluate_main
from dispatch.response import Response, XMLStatusResponse
from dispatch.view import View
from auth.decorators import *
from config.config import Config

class Intro(View):
	@login_required
	def handler(self, req, path):
		localvars = {}

		if not req.session['user'].is_admin:
			config = Config()
			base_url = config.base_url
			username = req.session['user'].name
			return Redirect(base_url + '/users/show/' + username)

		formatted = evaluate_main('intro.html', localvars, request=req)
		return Response(formatted)
