from template.shortcuts import evaluate_main
from dispatch.response import Response

class ErrorResponse(Response):
	def __init__(self, errormsg, request=None):
		localvars = {}
		localvars['errormsg'] = errormsg
		formatted = evaluate_main('error.html', localvars, request=request)
		Response.__init__(self, formatted)

