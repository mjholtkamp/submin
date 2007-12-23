from template.shortcuts import evaluate_main
from dispatch.response import Response

class ErrorResponse(Response):
	def __init__(self, errormsg):
		localvars = {}
		localvars['errormsg'] = errormsg
		formatted = evaluate_main('error', localvars)
		Response.__init__(self, formatted)

