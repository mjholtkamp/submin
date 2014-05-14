from submin.template.shortcuts import evaluate
from submin.dispatch.response import Response

def html_escape(data):
	data = data.replace('&', '&amp;')
	data = data.replace('<', '&lt;')
	data = data.replace('>', '&gt;')
	return data

class ErrorResponse(Response):
	def __init__(self, errormsg, request=None, details=None):
		localvars = {}
		localvars['errormsg'] = html_escape(errormsg)
		if details:
			localvars['details'] = html_escape(details)
		formatted = evaluate('error.html', localvars)

		Response.__init__(self, formatted)

