from template.shortcuts import evaluate_main
from template import evaluate
from dispatch.response import Response

class ErrorResponse(Response):
	def __init__(self, errormsg, request=None):
		localvars = {}
		localvars['errormsg'] = errormsg
		if request and request.session and 'user' in request.session:
			formatted = evaluate_main('error.html', localvars, request=request)
		else:
			formatted = evaluate('error.html', localvars)

		Response.__init__(self, formatted)

