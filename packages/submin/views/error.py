from submin.template.shortcuts import evaluate
from submin.dispatch.response import Response

class ErrorResponse(Response):
	def __init__(self, errormsg, request=None, details=None):
		localvars = {}
		localvars['errormsg'] = errormsg
		if details:
			localvars['details'] = details
		formatted = evaluate('error.html', localvars)

		Response.__init__(self, formatted)

